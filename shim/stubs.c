/* Minimal freestanding libc stubs for the sweet shim when built with clang/zig,
 * which does not inline __builtin_strcmp the way gcc does at -O2. */
#include <stdint.h>

int strcmp(const char *a, const char *b)
{
	while (*a && *a == *b)
		a++, b++;
	return (unsigned char)*a - (unsigned char)*b;
}

void *memcpy(void *d, const void *s, unsigned long n)
{
	unsigned char *dd = d;
	const unsigned char *ss = s;
	while (n--)
		*dd++ = *ss++;
	return d;
}

void *memset(void *d, int c, unsigned long n)
{
	unsigned char *dd = d;
	while (n--)
		*dd++ = (unsigned char)c;
	return d;
}
