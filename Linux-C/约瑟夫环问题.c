#include <stdio.h>
#include <malloc.h>
#include <stdlib.h>

#define N 8

typedef struct List
{
    int data;
    struct List *next;
}PNode, *PNode;

void creat_list(PNode *head)
{
    int i, n = 1;
    *PNode p1, p2, p3;
    (*head) =(*PNode)malloc(sizeof(PNode));
    (*head)->next = NULL;
    
    p1 = (*head);
    for(i = 0; i < N; i++)
    {
        p2 = (*PNode)malloc(sizeof(PNode));
        p2->data = n;
        P1->next = p2;
        p1 = p2;
        n++;
    }
    p1->next = NULL;
    p3 = (*head)->next;
    while(p3->next != NULL)
    {
        p3 = p3->next;
    }
    p3->next = (*head)->next;
}

void release(PNode *head, int m, int n)  //从第m个人开始报号，报到n
{
    PNode p1, p2，p3;
    p1 = (*head);
    
    for(int i = 0; i < m; i++)   
    {
        p1 = p1->next;
    }
    for(int j = 0; j < N -1; j++)  ////经过N-1次循环,链表中只剩下一个节点
    {
        for(int k = 0; k < n - 1; k++)
        {
            p1 = p1->next;      //找到需要删除节点的前驱节点
        }
        p2 = p1->next;   //p2为需要删除的结点
        p1->next = p2->next;
        free(p2);
        
        p1 = p1->next;   //从删除节点的下一个节点开始新一轮的循环
    }
    p3 = head->next;
    printf("最后的赢家是第%d号：", p3->data);
}


int main(void)
{
    *PNode Plist;
    creat_list(&Plist);
    release(&Plist, 1, 3);
}

