#include "../Apps/esp_rom_flasher.c"
#include <assert.h>
const t5_app_api_v1 *t5_app_get_api(uint32_t v) { (void)v; return NULL; }
const t5_ui_api_v1 *t5_ui_get_api(uint32_t v) { (void)v; return NULL; }
const t5_stream_api_v1 *t5_stream_get_api(uint32_t v) { (void)v; return NULL; }
const t5_program_esp_rom_api_v1 *t5_program_esp_rom_get_api(uint32_t v) { (void)v; return NULL; }
const t5_provider_capability_api_v1 *t5_provider_capability_get_api(uint32_t v) { (void)v; return NULL; }
static const char *input;
static size_t offset;
static unsigned reads, closes, programs;
static bool cancelled, stalled, oversized, missing;
static t5_program_esp_rom_result_t program_result;
static bool ui_poll(t5_ui_event_t *event, uint32_t wait) {
    (void)wait;
    if (!cancelled) return false;
    event->type=T5_UI_EVENT_BACK; return true;
}
static bool app_poll(t5_app_input_t *event, uint32_t wait) { (void)event;(void)wait;return false; }
static void draw(const t5_ui_chrome_t *chrome, const t5_ui_list_row_t *rows, uint32_t count, int32_t selected_row) {
    (void)chrome;(void)rows;(void)count;(void)selected_row;
}
static t5_stream_result_t seek_input(t5_stream_t stream, uint64_t pos) {
    assert(stream==1 && pos==0);offset=0;return T5_STREAM_OK;
}
static t5_stream_result_t read_input(t5_stream_t stream, void *out, uint32_t cap, uint32_t *count) {
    assert(stream==1);++reads;*count=0;
    if (oversized) { *count=cap+1;return T5_STREAM_OK; }
    if (stalled) return T5_STREAM_AGAIN;
    size_t n=strlen(input)-offset;
    if (n>7) n=7; /* Exercise tokens split across short stream reads. */
    assert(cap>=n);memcpy(out,input+offset,n);offset+=n;*count=(uint32_t)n;
    return offset==strlen(input)?T5_STREAM_EOF:T5_STREAM_OK;
}
static t5_stream_result_t open_input(const char *path, uint32_t flags, t5_stream_t *out) {
    assert(!strcmp(path,"/sd/firmware.bin") && flags==T5_STREAM_FILE_READ);
    *out=missing?0:1;return missing?T5_STREAM_IO:T5_STREAM_OK;
}
static t5_stream_result_t close_input(t5_stream_t stream) { assert(stream==1);++closes;return T5_STREAM_OK; }
static t5_program_esp_rom_result_t program(t5_stream_t stream, uint32_t size,
    t5_program_esp_rom_progress_fn progress, void *ctx, t5_program_esp_rom_status_v1 *status) {
    assert(stream==1 && size==32 && progress && !ctx);++programs;
    status->struct_size=sizeof(*status);strcpy(status->message,"mock provider failure");
    return program_result;
}
int main(void) {
    static const t5_ui_api_v1 ui_mock={.poll_event=ui_poll,.render_list=draw};
    static const t5_app_api_v1 app_mock={.poll=app_poll};
    static const t5_stream_api_v1 stream_mock={.read=read_input,.seek=seek_input,.open_file=open_input,.close=close_input};
    static const t5_program_esp_rom_api_v1 esp_mock={.program=program};
    ui=&ui_mock;app=&app_mock;streams=&stream_mock;
    const char *valid[]={"@4400 01 02 03 q","@FFFFF FF q","@4000 01 @4400 FF 00 Q"};
    const uint32_t totals[]={3,1,3};
    for (size_t i=0;i<3;++i) { uint32_t total=0;input=valid[i];assert(scan_titxt(1,&total));assert(total==totals[i] && offset==0); }
    const char *invalid[]={"", "q", "01 q", "@4000 0 q", "@4000 GG q", "@100000 FF q", "@FFFFF FF FF q", "@4000 01", "@4000 000000000000000000000000000000 q"};
    for (size_t i=0;i<sizeof(invalid)/sizeof(invalid[0]);++i) { uint32_t total=99;input=invalid[i];assert(!scan_titxt(1,&total));assert(total==99); }
    uint32_t total=0;input=valid[0];cancelled=true;assert(!scan_titxt(1,&total));cancelled=false;
    stalled=true;reads=0;assert(!scan_titxt(1,&total));assert(reads==16 && strstr(failure_text,"stalled"));stalled=false;
    oversized=true;assert(!scan_titxt(1,&total));oversized=false;
    assert(!flash_esp_selected()); /* No provider and no selected image. */
    esp_programmer=&esp_mock;image_count=1;selected=0;strcpy(images[0],"firmware.bin");image_sizes[0]=32;
    missing=true;assert(!flash_esp_selected());assert(!closes && !programs);missing=false;
    program_result=T5_PROGRAM_OK;assert(flash_esp_selected());assert(closes==1 && programs==1);
    program_result=(t5_program_esp_rom_result_t)-1;assert(!flash_esp_selected());assert(closes==2 && programs==2);assert(!strcmp(failure_text,"mock provider failure"));
    puts("Flasher input rejection, cancellation and mock ESP cleanup PASS");return 0;
}
