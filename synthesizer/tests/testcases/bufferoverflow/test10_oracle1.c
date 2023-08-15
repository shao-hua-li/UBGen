#include<stdlib.h>
#define init_arr_1(arr1, arr2, arr_type)   arr_type * arr1 = (arr_type*)malloc(sizeof(arr_type)*(sizeof(arr2) / sizeof(arr2[0])));  for(int i=0; i<(sizeof(arr2) / sizeof(arr2[0])); i++){     arr1[i] = arr2[i];   } 
#define init_arr_2(arr1, arr2, arr_type)   arr_type** arr1 = (arr_type**)malloc(sizeof(arr_type*)*(sizeof(arr2) / sizeof(arr2[0])));  for(int i=0; i<(sizeof(arr2) / sizeof(arr2[0])); i++){     arr1[i] = (arr_type*)malloc(sizeof(arr_type)*(sizeof(arr2[0]) / sizeof(arr2[0][0])));     for(int j=0; j<(sizeof(arr2[0]) / sizeof(arr2[0][0])); j++)       arr1[i][j] = arr2[i][j];   } 
#define init_arr_3(arr1, arr2, arr_type)   arr_type*** arr1 = (arr_type***)malloc(sizeof(arr_type**)*(sizeof(arr2) / sizeof(arr2[0])));  for(int i=0; i<(sizeof(arr2) / sizeof(arr2[0])); i++){     arr1[i] = (arr_type**)malloc(sizeof(arr_type*)*(sizeof(arr2[0]) / sizeof(arr2[0][0])));     for(int j=0; j<(sizeof(arr2[0]) / sizeof(arr2[0][0])); j++){       arr1[i][j] = (arr_type*)malloc(sizeof(arr_type)*(sizeof(arr2[0][0]) / sizeof(arr2[0][0][0])));       for(int k=0; k<(sizeof(arr2[0][0]) / sizeof(arr2[0][0][0])); k++)         arr1[i][j][k] = arr2[i][j][k];     }   } 
#define init_arr_1_uninit(arr1, arr2, arr_type)   arr_type * arr1 = (arr_type*)malloc(sizeof(arr_type)*(sizeof(arr2) / sizeof(arr2[0])));  
#define init_arr_2_uninit(arr1, arr2, arr_type)   arr_type** arr1 = (arr_type**)malloc(sizeof(arr_type*)*(sizeof(arr2) / sizeof(arr2[0])));  for(int i=0; i<(sizeof(arr2) / sizeof(arr2[0])); i++){     arr1[i] = (arr_type*)malloc(sizeof(arr_type)*(sizeof(arr2[0]) / sizeof(arr2[0][0])));   } 
#define init_arr_3_uninit(arr1, arr2, arr_type)   arr_type*** arr1 = (arr_type***)malloc(sizeof(arr_type**)*(sizeof(arr2) / sizeof(arr2[0])));  for(int i=0; i<(sizeof(arr2) / sizeof(arr2[0])); i++){     arr1[i] = (arr_type**)malloc(sizeof(arr_type*)*(sizeof(arr2[0]) / sizeof(arr2[0][0])));     for(int j=0; j<(sizeof(arr2[0]) / sizeof(arr2[0][0])); j++){       arr1[i][j] = (arr_type*)malloc(sizeof(arr_type)*(sizeof(arr2[0][0]) / sizeof(arr2[0][0][0])));     }   } 
#define free_1(arr)   free(arr);
#define free_2(arr)   for(int i=0; i<(sizeof(arr) / sizeof(arr[0])); i++){     free(arr[i]);   }   free(arr);
#define free_3(arr)   for(int i=0; i<(sizeof(arr) / sizeof(arr[0])); i++){     for(int j=0; j<(sizeof(arr[0]) / sizeof(arr[0][0])); j++){       free(arr[i][j]);     }     free(arr[i]);   }   free(arr);



#define _MUTPTR0 
#define _MUTPTR1 
#include<stdio.h>
int g1, g2[5];

int foo(int p) 

{
    



int *a = &g1;


    


int **b = &a;


    


int c;


    



c = *((*((b) _MUTPTR0)) +2/*UBFUZZ*/) + 1;
    

return c;
}



int main() {
    




int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
