# Function to count the number of successes
def count_success(data):
    success_count = {}
    for difficulty, results in data.items():
        success_count[difficulty] = results.count('Success')
    return success_count



# Counting successes
data = {'easy': ['Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success'], 
'inter': ['Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success'], 
'hard': ['Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success','Success', 'Success']}

ae = count_success(data)

data = {
    'easy': ['Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'There are 2 missing functions that need to be constructed in order to proceed further. These functions are required to complete the task.'], 
    'inter': ['Success', 'Success', 'Success', 'Success', "Error saving file: local variable 'argo_wf' referenced before assignment", 'Success', 'Success', 'Success', "There is a missing function that is required to send the PDF of the enhanced sketch of the castle surrounded by a dense forest to the colleague's email. Please construct the function to send emails.", 'There are 1 missing function(s) that need to be constructed in order to proceed with the task. The missing function should be able to perform the required task.'], 
    'hard': ['Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'There is a missing function that needs to be constructed in order to proceed with the task. The task requires converting the resized animation style image of the modern cityscape to JPEG format. Please create a function to handle this conversion.', 'There are 1 missing function(s) that need to be constructed in order to proceed with the task. The missing function should be able to perform the required task.']
}
ae_wo_c = count_success(data)


data = {'easy': ['Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success', "Error saving file: local variable 'argo_wf' referenced before assignment", 'Success', 'Success'], 
'inter': ['Success', 'Error saving file: local variable referenced before assignment', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success', 'Success'], 
'hard': ['Error saving file: local variable referenced before assignment', 'Success', 'Error saving file: local variable  referenced before assignment', 'Success', 'Success', 'Success', 'Success', 'Success', "Error saving file: local variable 'argo_wf' referenced before assignment", 'Error saving file: local variable referenced before assignment']}
we_wo_d_c = count_success(data)
# Display the result


print(ae)
print("-"*40)
print(ae_wo_c)
print("-"*40)
print(we_wo_d_c)