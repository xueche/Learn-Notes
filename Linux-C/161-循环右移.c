#include<stdio.h>

unsigned int roate_right(unsigned int x, int n)
{
    /*unsigned int m = 1;
    int i;
    for(i = 0; i < n; i++){
        m = (m << i) | m;
    }*/
    unsigned int y;
	y = (x << (32-n) | (x >> n);
    return y;
}

int main()
{
    printf("%x\n", roate_right(0xdeadbeef, 16));
    return 0;
}