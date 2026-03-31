# Gets bases, like Eboot base or LibKernel base and other
    "get_sys_bases": """
-- Displays EBOOT, LIBC, FIOS, libkernel, JIT bases, firmware version, and jailbreak status.

-- Made for people to learn from, to mod and make it better, to use in their projects.
local function to_hex(val)
    if not val then return "nil" end
    return string.format("0x%016X", val)
end

-- Get firmware version
local fw_version = FW_VERSION
if not fw_version and get_fwversion then
    fw_version = get_fwversion()
end

-- Determine platform if not already known
local platform = PLATFORM
if not platform and LIBC_BASE and read64 then
    local addr = read64(LIBC_BASE + 0xCBDA8) -- sceKernelGetModuleInfoFromAddr
    local mod_info = malloc(0x300)
    local ret = sceKernelGetModuleInfoFromAddr(addr, 1, mod_info)
    if ret == 0 then
        local init_proc = read64(mod_info + 0x128)
        local libkernel_base = read64(mod_info + 0x160)
        local delta = init_proc - libkernel_base
        if delta == 0x0 then platform = "PS4"
        elseif delta == 0x10 then platform = "PS5"
        else platform = "Unknown"
        end
    else
        platform = "Unknown"
    end
    free(mod_info)
end

-- Get libkernel base
local libkernel_base = LIBKERNEL_BASE
if not libkernel_base and LIBC_BASE and read64 then
    local addr = read64(LIBC_BASE + 0xCBDA8)
    local mod_info = malloc(0x300)
    local ret = sceKernelGetModuleInfoFromAddr(addr, 1, mod_info)
    if ret == 0 then
        libkernel_base = read64(mod_info + 0x160)
    end
    free(mod_info)
end

-- Get JIT base if available
local jit_base = JIT_BASE
if not jit_base and BRIDGE_BASE and DOOR3_SHM then
    jit_base = read64(DOOR3_SHM) - 0x1B41E8
end

-- Check jailbreak status
local jailbroken = false
if is_jailbroken then
    jailbroken = is_jailbroken()
elseif syscall and syscall.getuid then
    local uid = syscall.getuid()
    local sandbox = syscall.is_in_sandbox and syscall.is_in_sandbox() or 1
    jailbroken = (uid == 0 and sandbox == 0)
end

-- Get current IP
local current_ip = nil
if get_current_ip then
    current_ip = get_current_ip()
end

local msg = string.format([[
=== System Info ===
Platform   : %s
FW Version : %s
Jailbroken : %s
EBOOT Base : %s
LIBC Base  : %s
FIOS Base  : %s
Libkernel  : %s
JIT Base   : %s
Current IP : %s
===================
]],
    tostring(platform or "Unknown"),
    tostring(fw_version or "Unknown"),
    tostring(jailbroken and "Yes" or "No"),
    to_hex(EBOOT_BASE),
    to_hex(LIBC_BASE),
    to_hex(FIOS_BASE),
    to_hex(libkernel_base),
    to_hex(jit_base),
    tostring(current_ip or "Not connected")
)
-- Show dialog
if show_dialog then
    show_dialog(msg)
else
    send_notification(msg)
end
""",
