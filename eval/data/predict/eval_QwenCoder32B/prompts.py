FEW_SHOT_CoT_SYSTEM_PROMPT = '''
Your task is to create Argo HTTP DAG workflows in YAML format based on user queries and available API information. 

Follow these specific guidelines when generating the YAML file:
1. For each parameter in the workflow:
- If the parameter value is dependent on the result of another API, use the format: 
`{{{{ tasks.<dependency API name>.result }}}}`.
Example:
```yaml
- name: weather
value: '{{{{ tasks.checkweather.result }}}}'
```

- If the parameter value is independent and comes from user input, use the format:
`{{{{ inputs.parameters.<parameter name> }}}}`.
Example:
```yaml
- name: occasion
value: '{{{{ inputs.parameters.occasion }}}}'
```

2. Ensure the workflow is generated in a valid Argo YAML format without any additional text.

Here are some examples of queries and the corresponding workflows:

Example 1:
User Query: 'sarah_wilson' wants to reserve the book 'Moby-Dick'. Start from September 12th to September 26th.
Output:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
generateName: dependency-workflow-22-
spec:
entrypoint: main
templates:
- name: main
dag:
tasks:
- name: username2email
    template: username2email
    dependencies:
    - title2isbn
    arguments:
    parameters:
    - name: username
        value: '{{ inputs.parameters.username }}'
- name: title2isbn
    template: title2isbn
    arguments:
    parameters:
    - name: title
        value: '{{ inputs.parameters.title }}'
- name: reservebook
    template: reservebook
    dependencies:
    - username2email
    arguments:
    parameters:
    - name: user_email
        value: '{{ tasks.username2email.result }}'
    - name: ISBN
        value: '{{ tasks.title2isbn.result }}'
    - name: start_date
        value: '{{ inputs.parameters.start_date }}'
    - name: end_date
        value: '{{ inputs.parameters.end_date }}'
```

Example 2:
User Query: Can you book a flight from my city to New York on May 15th?
Output:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
generateName: dependency-workflow-1542-
spec:
entrypoint: main
templates:
- name: main
dag:
tasks:
- name: findflight
    template: findflight
    dependencies:
    - fetchcity
    arguments:
    parameters:
    - name: cityDeparture
        value: '{{ tasks.fetchcity.result }}'
    - name: cityArrival
        value: '{{ inputs.parameters.cityArrival }}'
    - name: date
        value: '{{ inputs.parameters.date }}'
- name: bookflight
    template: bookflight
    dependencies:
    - fetchflightid
    arguments:
    parameters:
    - name: flight_ID
        value: '{{ tasks.fetchflightid.result }}'
    - name: date
        value: '{{ inputs.parameters.date }}'
- name: getuserid
    template: getuserid
    arguments:
    parameters:
    - name: username
        value: '{{ inputs.parameters.username }}'
- name: fetchflightid
    template: fetchflightid
    dependencies:
    - findflight
    arguments:
    parameters:
    - name: flight_name
        value: '{{ tasks.findflight.result }}'
- name: fetchcity
    template: fetchcity
    dependencies:
    - getuserid
    arguments:
    parameters:
    - name: user_ID
        value: '{{ tasks.getuserid.result }}'```
            '''


FEW_SHOT_CoT_USER_PROMPT = """
User Query: {query}
APIs: {topk_functions}
#write a argo workflow in YAML format. Lets think step by step:
            """

FEW_SHOT_SYSTEM_PROMPT = '''
Your task is to create Argo HTTP DAG workflows in YAML format based on user queries and available API information. 

Follow these specific guidelines when generating the YAML file:
1. For each parameter in the workflow:
- If the parameter value is dependent on the result of another API, use the format: 
`{{{{ tasks.<dependency API name>.result }}}}`.
Example:
```yaml
- name: weather
value: '{{{{ tasks.checkweather.result }}}}'
```

- If the parameter value is independent and comes from user input, use the format:
`{{{{ inputs.parameters.<parameter name> }}}}`.
Example:
```yaml
- name: occasion
value: '{{{{ inputs.parameters.occasion }}}}'
```

2. Ensure the workflow is generated in a valid Argo YAML format without any additional text.

Here are some examples of queries and the corresponding workflows:

Example 1:
User Query: 'sarah_wilson' wants to reserve the book 'Moby-Dick'. Start from September 12th to September 26th.
Output:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
generateName: dependency-workflow-22-
spec:
entrypoint: main
templates:
- name: main
dag:
tasks:
- name: username2email
    template: username2email
    dependencies:
    - title2isbn
    arguments:
    parameters:
    - name: username
        value: '{{ inputs.parameters.username }}'
- name: title2isbn
    template: title2isbn
    arguments:
    parameters:
    - name: title
        value: '{{ inputs.parameters.title }}'
- name: reservebook
    template: reservebook
    dependencies:
    - username2email
    arguments:
    parameters:
    - name: user_email
        value: '{{ tasks.username2email.result }}'
    - name: ISBN
        value: '{{ tasks.title2isbn.result }}'
    - name: start_date
        value: '{{ inputs.parameters.start_date }}'
    - name: end_date
        value: '{{ inputs.parameters.end_date }}'
```

Example 2:
User Query: Can you book a flight from my city to New York on May 15th?
Output:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
generateName: dependency-workflow-1542-
spec:
entrypoint: main
templates:
- name: main
dag:
tasks:
- name: findflight
    template: findflight
    dependencies:
    - fetchcity
    arguments:
    parameters:
    - name: cityDeparture
        value: '{{ tasks.fetchcity.result }}'
    - name: cityArrival
        value: '{{ inputs.parameters.cityArrival }}'
    - name: date
        value: '{{ inputs.parameters.date }}'
- name: bookflight
    template: bookflight
    dependencies:
    - fetchflightid
    arguments:
    parameters:
    - name: flight_ID
        value: '{{ tasks.fetchflightid.result }}'
    - name: date
        value: '{{ inputs.parameters.date }}'
- name: getuserid
    template: getuserid
    arguments:
    parameters:
    - name: username
        value: '{{ inputs.parameters.username }}'
- name: fetchflightid
    template: fetchflightid
    dependencies:
    - findflight
    arguments:
    parameters:
    - name: flight_name
        value: '{{ tasks.findflight.result }}'
- name: fetchcity
    template: fetchcity
    dependencies:
    - getuserid
    arguments:
    parameters:
    - name: user_ID
        value: '{{ tasks.getuserid.result }}'```
            '''


FEW_SHOT_USER_PROMPT = """
User Query: {query}
APIs: {topk_functions}
#write a argo workflow in YAML format. Lets think step by step:
            """


ZERO_SHOT_COT_SYSTEM_PROMPT = '''
Your task is to create Argo HTTP DAG workflows in YAML format based on user queries and available API information. 

Follow these specific guidelines when generating the YAML file:
1. For each parameter in the workflow:
- If the parameter value is dependent on the result of another API, use the format: 
`{{{{ tasks.<dependency API name>.result }}}}`.
Example:
```yaml
- name: weather
value: '{{{{ tasks.checkweather.result }}}}'
```

- If the parameter value is independent and comes from user input, use the format:
`{{{{ inputs.parameters.<parameter name> }}}}`.
Example:
```yaml
- name: occasion
value: '{{{{ inputs.parameters.occasion }}}}'
```

2. Ensure the workflow is generated in a valid Argo YAML format without any additional text.

Here are some examples of queries and the corresponding workflows:

Example 1:
User Query: 'sarah_wilson' wants to reserve the book 'Moby-Dick'. Start from September 12th to September 26th.
Output:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
generateName: dependency-workflow-22-
spec:
entrypoint: main
templates:
- name: main
dag:
tasks:
- name: username2email
    template: username2email
    dependencies:
    - title2isbn
    arguments:
    parameters:
    - name: username
        value: '{{ inputs.parameters.username }}'
- name: title2isbn
    template: title2isbn
    arguments:
    parameters:
    - name: title
        value: '{{ inputs.parameters.title }}'
- name: reservebook
    template: reservebook
    dependencies:
    - username2email
    arguments:
    parameters:
    - name: user_email
        value: '{{ tasks.username2email.result }}'
    - name: ISBN
        value: '{{ tasks.title2isbn.result }}'
    - name: start_date
        value: '{{ inputs.parameters.start_date }}'
    - name: end_date
        value: '{{ inputs.parameters.end_date }}'
```

Example 2:
User Query: Can you book a flight from my city to New York on May 15th?
Output:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
generateName: dependency-workflow-1542-
spec:
entrypoint: main
templates:
- name: main
dag:
tasks:
- name: findflight
    template: findflight
    dependencies:
    - fetchcity
    arguments:
    parameters:
    - name: cityDeparture
        value: '{{ tasks.fetchcity.result }}'
    - name: cityArrival
        value: '{{ inputs.parameters.cityArrival }}'
    - name: date
        value: '{{ inputs.parameters.date }}'
- name: bookflight
    template: bookflight
    dependencies:
    - fetchflightid
    arguments:
    parameters:
    - name: flight_ID
        value: '{{ tasks.fetchflightid.result }}'
    - name: date
        value: '{{ inputs.parameters.date }}'
- name: getuserid
    template: getuserid
    arguments:
    parameters:
    - name: username
        value: '{{ inputs.parameters.username }}'
- name: fetchflightid
    template: fetchflightid
    dependencies:
    - findflight
    arguments:
    parameters:
    - name: flight_name
        value: '{{ tasks.findflight.result }}'
- name: fetchcity
    template: fetchcity
    dependencies:
    - getuserid
    arguments:
    parameters:
    - name: user_ID
        value: '{{ tasks.getuserid.result }}'```
            '''

ZERO_SHOT_COT_USER_PROMPT = """
User Query: {query}
APIs: {topk_functions}
#write a argo workflow in YAML format. Lets think step by step:
            """

ZERO_SHOT_SYSTEM_PROMPT = '''
Your task is to create Argo HTTP DAG workflows in YAML format based on user queries and available API information. 

Follow these specific guidelines when generating the YAML file:
1. For each parameter in the workflow:
- If the parameter value is dependent on the result of another API, use the format: 
`{{{{ tasks.<dependency API name>.result }}}}`.
Example:
```yaml
- name: weather
value: '{{{{ tasks.checkweather.result }}}}'
```

- If the parameter value is independent and comes from user input, use the format:
`{{{{ inputs.parameters.<parameter name> }}}}`.
Example:
```yaml
- name: occasion
value: '{{{{ inputs.parameters.occasion }}}}'
```

2. Ensure the workflow is generated in a valid Argo YAML format without any additional text.

Here are some examples of queries and the corresponding workflows:

Example 1:
User Query: 'sarah_wilson' wants to reserve the book 'Moby-Dick'. Start from September 12th to September 26th.
Output:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
generateName: dependency-workflow-22-
spec:
entrypoint: main
templates:
- name: main
dag:
tasks:
- name: username2email
    template: username2email
    dependencies:
    - title2isbn
    arguments:
    parameters:
    - name: username
        value: '{{ inputs.parameters.username }}'
- name: title2isbn
    template: title2isbn
    arguments:
    parameters:
    - name: title
        value: '{{ inputs.parameters.title }}'
- name: reservebook
    template: reservebook
    dependencies:
    - username2email
    arguments:
    parameters:
    - name: user_email
        value: '{{ tasks.username2email.result }}'
    - name: ISBN
        value: '{{ tasks.title2isbn.result }}'
    - name: start_date
        value: '{{ inputs.parameters.start_date }}'
    - name: end_date
        value: '{{ inputs.parameters.end_date }}'
```

Example 2:
User Query: Can you book a flight from my city to New York on May 15th?
Output:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
generateName: dependency-workflow-1542-
spec:
entrypoint: main
templates:
- name: main
dag:
tasks:
- name: findflight
    template: findflight
    dependencies:
    - fetchcity
    arguments:
    parameters:
    - name: cityDeparture
        value: '{{ tasks.fetchcity.result }}'
    - name: cityArrival
        value: '{{ inputs.parameters.cityArrival }}'
    - name: date
        value: '{{ inputs.parameters.date }}'
- name: bookflight
    template: bookflight
    dependencies:
    - fetchflightid
    arguments:
    parameters:
    - name: flight_ID
        value: '{{ tasks.fetchflightid.result }}'
    - name: date
        value: '{{ inputs.parameters.date }}'
- name: getuserid
    template: getuserid
    arguments:
    parameters:
    - name: username
        value: '{{ inputs.parameters.username }}'
- name: fetchflightid
    template: fetchflightid
    dependencies:
    - findflight
    arguments:
    parameters:
    - name: flight_name
        value: '{{ tasks.findflight.result }}'
- name: fetchcity
    template: fetchcity
    dependencies:
    - getuserid
    arguments:
    parameters:
    - name: user_ID
        value: '{{ tasks.getuserid.result }}'```
            '''


ZERO_SHOT_USER_PROMPT = """
User Query: {query}
APIs: {topk_functions}
#write a argo workflow in YAML format. Lets think step by step:
            """