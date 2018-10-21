#include<stdio.h>
#include<string.h>

//位运算实现无符号整形的乘法
unsigned int multiply(unsigned int x, unsigned int y)
{
    int i = 0, a[32];
	memset(a, -1, sizeof(a));
    unsigned int m = 0x1;
    
    while(y){
        if (y & m)
            a[i]= i;
        i++;
        y = y >> 1;
    }
    
    unsigned int result = 0;
    int j;
    for (j = 0 ; j < 32; j++){
        if(a[j] != -1)
            result = result + (x << a[j]);
    }
    return result;
}

int main(void)
{
    unsigned int x, y;
	while(1){
    printf("请输入两个无符号整数:\n");
    scanf("%u%u", &x, &y);
    printf("%u * %u = %u\n", x, y, multiply(x, y));
	}
    return 0;
}