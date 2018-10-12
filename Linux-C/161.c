#include<stdio.h>

//统计无符号整数的二进制表示中1的个数（汉明重量）
int countbit(unsigned int x)
{
    unsigned int a = 0x1;
    int count = 0;
    while(x){
        if(x & a)
            count++;
        x = (x >> 1);
    }
    return count;
}

int main(void)
{
    unsigned int a;
    printf("请输入一个整数:\n");
    scanf(%d,&a);
    printf("%d的二进制表示中1的个数为:%d\n",a,countbit(a));
    retunr 0;
}