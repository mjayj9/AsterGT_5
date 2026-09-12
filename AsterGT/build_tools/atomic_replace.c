#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <wchar.h>

/* One-volume atomic replacement. No remove-then-rename fallback. */
int wmain(int argc, wchar_t **argv) {
    wchar_t source[32768], target[32768];
    if (argc != 3) return ERROR_INVALID_PARAMETER;
    if (!GetFullPathNameW(argv[1],32768,source,NULL) || !GetFullPathNameW(argv[2],32768,target,NULL))
        return ERROR_BAD_PATHNAME;
    wchar_t *s=wcsrchr(source,L'\\'), *t=wcsrchr(target,L'\\');
    if (!s || !t || s-source!=t-target || _wcsnicmp(source,target,s-source)!=0)
        return ERROR_NOT_SAME_DEVICE;
    size_t n=wcslen(source);
    if(n<4 || _wcsicmp(source+n-4,L".tmp")!=0 || _wcsicmp(source,target)==0)
        return ERROR_INVALID_PARAMETER;
    HANDLE h=CreateFileW(source,GENERIC_WRITE,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
    if(h==INVALID_HANDLE_VALUE) return (int)GetLastError();
    BOOL flushed=FlushFileBuffers(h);DWORD flush_error=GetLastError();CloseHandle(h);
    if(!flushed) return (int)flush_error;
    BOOL ok;
    if(GetFileAttributesW(target)!=INVALID_FILE_ATTRIBUTES)
        ok=ReplaceFileW(target,source,NULL,0,NULL,NULL);
    else
        ok=MoveFileExW(source,target,MOVEFILE_WRITE_THROUGH);
    return ok ? 0 : (int)GetLastError();
}
