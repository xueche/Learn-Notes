#include <stdio.h>

//测试小端字节序还是大端字节序
int main(){
    union{
        char a;
        int b;
    }s;
    s.b = 0x02000001;
    printf("%x\n", (int)s.a);
    
    return 0;
}