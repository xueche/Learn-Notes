#include <stdio.h>

int stack[512];
int top = 0;

void push(char c)
{
    stack[top++] = c;
}

char pop(void)
{
    return stack[--top];
}

int is_empty(void)
{
    return top == 0;   //若top为0，返回true;反之返回false
}

int main(void)
{
    push('a');
    push('b');
    push('c');
    
    while(!is_empty()){
        putchar(pop());
        printf("\ta=%d\n", is_empty());
    }
    
    
    putchar('\n');
    
    return 0;
}