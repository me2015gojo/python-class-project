# test_dict={'ME':2,'best':2,'for':2, 'good':1}
# print("the original : " + str(test_dict))
# K=2
# res=0
# for key in test_dict:
#     if test_dict[key]==K:
#         res=res+1
# print("Frequency of K is :" + str(res))


student_data={
"id1":
{"name":"Sara","class":  "v","subject_integration":"english,math,science"},
"id2":
{"name":"david","class":  "v","subject_integration":"english,math,science"},
"id3":
{"name":"Sara","class":  "v","subject_integration":"english,math,science"},
"id4":
{"name":"Jay","class":  "v","subject_integration":"english,math,science"},
}
result={}
seen_keys=[]

for student_id, details in student_data.items():
    unique_key=(details["name"],details["class"],details["subject_integration"])  
    if  unique_key not in seen_keys :
        seen_keys.append(unique_key) 
        result[student_id]=details
for k,v in result.items():
    print(k, ":", v) 