#include <stdio.h>

bool find(int (*a)[4], int target)  //数组指针(*a)[]作为函数形参，直接将二维数组名传入
{
    int row, col, i, j;
    bool found = false;
    col = sizeof(a[0])/sizeof(int);
    row = sizeof(a);  //此时二维数组名已经退化为指针，指向数组首元素
	printf("%d,%d,%d\n", col,row,a[1][1]);  //row的值为4
    i = 0;
    j = col - 1;
    while(i < row && j >= 0){
        if(a[i][j] == target){
            found = true;
            break;
        }
        if(a[i][j] < target)
            i++;
        else 
            j--;
    }
    return found;    
}

int main(void)
{
    int a[4][4] = {{1,3,5,7}, {2,4,7,10}, {3,7,9,13}, {4,9,12,15}};
	//printf("%d\n",sizeof(a));
	if (find(a, 8))
        printf("Found the number\n");
    else
        printf("Not found\n");
	
	return 0;
}