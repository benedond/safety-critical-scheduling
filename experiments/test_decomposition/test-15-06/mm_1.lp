\ Model Master Model
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  24.1552774661804 alpha[0] + 40.74206577391397 alpha[1]
   + 43.22431913467773 alpha[2] + 10.95523251961618 alpha[3]
   + 8.014935065792852 alpha[4] + 23.71579255477492 alpha[5]
   + 61.04304834152236 alpha[6] + 55.23353604139308 alpha[7]
   + 11.267331888547 alpha[8] + 39.74402831884903 alpha[9]
   + 45.5535406189783 alpha[10] + 97.27233226294314 alpha[11]
   + 38.32881786949133 alpha[12] + 25.36532442167705 alpha[13]
   + 27.53429649011538 alpha[14] + 39.96514060504384 alpha[15]
   + 162.6442103983229 alpha[16] + 169.6635443494037 alpha[17]
   + 10.95523251961618 alpha[18] + 69.59393498794222 alpha[19]
   + 38.35274711833235 alpha[20] + 64.72236297159684 alpha[21]
   + 63.97858024279267 alpha[22] + 111.5353722086031 alpha[23]
   + 54.58571495658104 alpha[24] + 75.5114070864222 alpha[25]
   + 32.90088716487016 alpha[26] + 111.2859597320835 alpha[27]
Subject To
 C_major_frame: 20 alpha[0] + 86 alpha[1] + 51 alpha[2] + 23 alpha[3]
   + 18 alpha[4] + 86 alpha[5] + 46 alpha[6] + 46 alpha[7] + 7 alpha[8]
   + 45 alpha[9] + 45 alpha[10] + 57 alpha[11] + 33 alpha[12]
   + 44 alpha[13] + 23 alpha[14] + 52 alpha[15] + 78 alpha[16]
   + 93 alpha[17] + 23 alpha[18] + 51 alpha[19] + 41 alpha[20]
   + 41 alpha[21] + 86 alpha[22] + 80 alpha[23] + 49 alpha[24]
   + 49 alpha[25] + 20 alpha[26] + 81 alpha[27] <= 418
 C_task_cover_task-0: alpha[1] + alpha[3] + alpha[12] + alpha[14]
   + alpha[17] + alpha[18] >= 1
 C_task_cover_task-1: alpha[6] + alpha[10] + alpha[13] + alpha[15]
   + alpha[16] >= 1
 C_task_cover_task-2: alpha[6] + alpha[7] + alpha[11] + alpha[17]
   + alpha[25] >= 1
 C_task_cover_task-3: alpha[17] + alpha[24] + alpha[25] >= 1
 C_task_cover_task-4: alpha[12] + alpha[15] + alpha[16] + alpha[19]
   + alpha[21] >= 1
 C_task_cover_task-5: alpha[23] + alpha[27] >= 1
 C_task_cover_task-6: alpha[11] + alpha[20] + alpha[21] + alpha[22] >= 1
 C_task_cover_task-7: alpha[4] + alpha[16] >= 1
 C_task_cover_task-8: alpha[1] + alpha[5] + alpha[9] + alpha[10]
   + alpha[22] + alpha[24] >= 1
 C_task_cover_task-9: alpha[23] + alpha[27] >= 1
 C_task_cover_task-10: alpha[23] + alpha[27] >= 1
 C_task_cover_task-11: alpha[8] + alpha[14] + alpha[26] >= 1
 C_task_cover_task-12: alpha[11] + alpha[20] + alpha[21] + alpha[22] >= 1
 C_task_cover_task-13: alpha[2] + alpha[19] >= 1
 C_task_cover_task-14: alpha[0] + alpha[26] >= 1
Bounds
 alpha[0] <= 1
 alpha[1] <= 1
 alpha[2] <= 1
 alpha[3] <= 1
 alpha[4] <= 1
 alpha[5] <= 1
 alpha[6] <= 1
 alpha[7] <= 1
 alpha[8] <= 1
 alpha[9] <= 1
 alpha[10] <= 1
 alpha[11] <= 1
 alpha[12] <= 1
 alpha[13] <= 1
 alpha[14] <= 1
 alpha[15] <= 1
 alpha[16] <= 1
 alpha[17] <= 1
 alpha[18] <= 1
 alpha[19] <= 1
 alpha[20] <= 1
 alpha[21] <= 1
 alpha[22] <= 1
 alpha[23] <= 1
 alpha[24] <= 1
 alpha[25] <= 1
 alpha[26] <= 1
 alpha[27] <= 1
End
