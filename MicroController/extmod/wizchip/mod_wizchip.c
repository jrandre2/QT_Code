// mod_wizchip.c
//
// Minimal MicroPython module wrapping selected functions from the official WIZnet driver
// (from the WIZnet-PICO-v6-C repository) for the W6100-EVB-Pico2.
// Based on the official driver functions, this module wraps:
//   - wizchip_sw_reset()
//   - wizchip_init()
//   - wizchip_get_ip(uint8_t ip[4])
//   - wizchip_set_ip(uint8_t ip[4])


#include "py/obj.h"
#include "py/runtime.h"
#include "wizchip_conf.h"  // Include the official driver header (adjust path as needed)
#include <string.h>
#include <stdio.h>

//------------------------------------------------------------------------------
// wizchip.reset()
//------------------------------------------------------------------------------
STATIC mp_obj_t wizchip_reset(void) {
    wizchip_sw_reset();
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(wizchip_reset_obj, wizchip_reset);

//------------------------------------------------------------------------------
// wizchip.init()
//------------------------------------------------------------------------------
STATIC mp_obj_t wizchip_init(void) {
    int ret = wizchip_init();
    if (ret != 0) {
        mp_raise_OSError(ret);
    }
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(wizchip_init_obj, wizchip_init);

//------------------------------------------------------------------------------
// wizchip.get_ip()
//------------------------------------------------------------------------------
STATIC mp_obj_t wizchip_get_ip(void) {
    uint8_t ip[4] = {0,0,0,0};
    wizchip_get_ip(ip);
    char ip_str[16];
    snprintf(ip_str, sizeof(ip_str), "%d.%d.%d.%d", ip[0], ip[1], ip[2], ip[3]);
    return mp_obj_new_str(ip_str, strlen(ip_str));
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(wizchip_get_ip_obj, wizchip_get_ip);

//------------------------------------------------------------------------------
// wizchip.set_ip(ip)
//------------------------------------------------------------------------------
STATIC mp_obj_t wizchip_set_ip(mp_obj_t ip_obj) {
    const char *ip_str = mp_obj_str_get_str(ip_obj);
    uint8_t ip[4];
    if (sscanf(ip_str, "%hhu.%hhu.%hhu.%hhu", &ip[0], &ip[1], &ip[2], &ip[3]) != 4) {
        mp_raise_ValueError("Invalid IP format");
    }
    wizchip_set_ip(ip);
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(wizchip_set_ip_obj, wizchip_set_ip);

//------------------------------------------------------------------------------
// Module Globals
//------------------------------------------------------------------------------
STATIC const mp_rom_map_elem_t wizchip_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_wizchip) },
    { MP_ROM_QSTR(MP_QSTR_reset), MP_ROM_PTR(&wizchip_reset_obj) },
    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&wizchip_init_obj) },
    { MP_ROM_QSTR(MP_QSTR_get_ip), MP_ROM_PTR(&wizchip_get_ip_obj) },
    { MP_ROM_QSTR(MP_QSTR_set_ip), MP_ROM_PTR(&wizchip_set_ip_obj) },
};

STATIC MP_DEFINE_CONST_DICT(wizchip_module_globals, wizchip_module_globals_table);

const mp_obj_module_t wizchip_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&wizchip_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_wizchip, wizchip_user_cmodule, MODULE_WIZCHIP_ENABLED);
