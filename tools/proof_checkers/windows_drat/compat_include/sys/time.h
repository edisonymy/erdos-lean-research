/* Minimal POSIX gettimeofday compatibility for the pinned DRAT-trim sources.
   This file is isolated from, and does not modify, third_party/drat-trim. */
#ifndef WINDOWS_DRAT_COMPAT_SYS_TIME_H
#define WINDOWS_DRAT_COMPAT_SYS_TIME_H

#include <winsock2.h> /* supplies struct timeval on Windows */
#include <windows.h>

/* The upstream checker owns these names for its result codes. */
#ifdef ERROR
#undef ERROR
#endif
#ifdef FAILED
#undef FAILED
#endif

static int gettimeofday(struct timeval *tv, void *tz) {
    FILETIME file_time;
    ULARGE_INTEGER ticks;
    unsigned long long unix_ticks;
    (void)tz;
    GetSystemTimeAsFileTime(&file_time);
    ticks.LowPart = file_time.dwLowDateTime;
    ticks.HighPart = file_time.dwHighDateTime;
    unix_ticks = ticks.QuadPart - 116444736000000000ULL;
    tv->tv_sec = (long)(unix_ticks / 10000000ULL);
    tv->tv_usec = (long)((unix_ticks % 10000000ULL) / 10ULL);
    return 0;
}

/* DRAT-trim uses the POSIX spelling only for buffered reads. */
#ifndef getc_unlocked
#define getc_unlocked getc
#endif

#endif
