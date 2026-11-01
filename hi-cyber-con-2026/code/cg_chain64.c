#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

/* Read lines "M S CYCLES" (decimal uint64). Output "V" per line.
   Chain: V = S; repeat CYCLES times: V = V*V mod M */
int main(void){
    char line[512];
    while (fgets(line, sizeof line, stdin)) {
        unsigned long long M, S, C, i;
        if (sscanf(line, "%llu %llu %llu", &M, &S, &C) != 3) continue;
        unsigned __int128 V = S % M;
        for (i = 0; i < C; i++) {
            V = (V * V) % M;
        }
        printf("%llu\n", (unsigned long long)V);
        fflush(stdout);
    }
    return 0;
}
