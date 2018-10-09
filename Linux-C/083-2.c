# include <stdio.h>
# include <stdlib.h>
# include <time.h>
# define N 20

int randon_array[N];

 void produce_random(int upper_bound)
{
     int i;
	 srand(time(NULL));
    for (i = 0; i < N; i++)
    {
        randon_array[i] = rand()% upper_bound;
    }
}

int max_value(int a[])
{
    int i;
    int max = a[0];

    for (i = 1; i < 10; i++)
    {
        if(max < a[i])
            max = a[i];
        
    }
	return max;
}

void print_histogram (int a[])
{
	int m, n, i, max;
	for(i = 0; i < 10; i++)
        printf("%d\t", i);
    printf("\n");
	max = max_value(a);
    for (m = 1; m <= max; m++)
    {
        for(n = 0; n < 10; n++)
		{
            if (a[n] > 0)
            {
                printf("*\t");
                a[n]--;
            }
			else
				printf("\t");
		}
            
    }
	printf("\n");    
}

int main(void)
{
    int histogram[10] = {0}, i, j;
	produce_random(10);
	for (i = 0; i < N; i++)
		histogram[randon_array[i]]++;
    printf("Value\thowmany\n");
    for (j = 0; j < 10; j++)
        printf("%d\t%d\n", j, histogram[j]);
	printf("\n");
    print_histogram(histogram);
    return 0;
    
}