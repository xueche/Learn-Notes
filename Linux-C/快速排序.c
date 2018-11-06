#include <stdio.h>

# define SIZE 7


int fast_sort(int a[], int start, int end)
{
    int i = start;
    int j = end;
    int key = a[start];
    
    while(i < j)
    {
        while(i < j && a[j] >= key)
            j--;
        while(i < j && a[i] <= key)
            i++;
        if(i < j)
        {
            int temp = a[j];
            a[j] = a[i];
            a[i] = temp;
        }
    }
    a[start] = a[i];
    a[i] = key;
    
    for(int k = 0; k < SIZE; k++)
        printf("%d\t",a[k]);
    putchar('\n');
    
    return i;
}

void rec_sort(int a[], int begin, int end)
{
    if(begin > end)
        return;
    int mid;
    mid = fast_sort(a, begin, end);
    rec_sort(a, begin, mid-1);
    rec_sort(a, mid+1, end);
}

int main(void)
{
    int a[SIZE] = {9, 12, 5, 9, 5, 13, 6};
    rec_sort(a, 0, SIZE-1);
    return 0;
}