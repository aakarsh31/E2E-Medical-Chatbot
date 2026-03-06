test_questions = [
    # Direct factual
    {
        "user_input": "What is diabetes mellitus?",
        "reference": "Diabetes mellitus is a chronic disease characterized by the inability of the body to properly absorb glucose into its cells, resulting in elevated blood glucose levels. It can cause serious complications including kidney failure, heart disease, stroke, and blindness.",
        "type": "direct"
    },
    {
        "user_input": "What are the symptoms of hypoglycemia?",
        "reference": "Symptoms of hypoglycemia include feeling hungry, cranky, confused, and tired, as well as sweating and shakiness. If untreated it can lead to loss of consciousness or seizures.",
        "type": "direct"
    },
    {
        "user_input": "What medications are used to treat Type 2 diabetes?",
        "reference": "Type 2 diabetes is treated with oral medications including sulfonylureas such as glyburide, glipizide, and glimepiride, as well as metformin, acarbose, and troglitizone. In some cases insulin injections are required.",
        "type": "direct"
    },
    {
        "user_input": "What are the side effects of metformin?",
        "reference": "Common side effects of metformin include mild diarrhea, nausea, vomiting, and stomach cramps. Less common side effects include sore mouth and vaginal itching.",
        "type": "direct"
    },
    # Inference/reasoning
    {
        "user_input": "Why does Type 1 diabetes require insulin injections but Type 2 often does not?",
        "reference": "Type 1 diabetes is an autoimmune disorder where the pancreas produces little or no insulin, making external insulin injections necessary. In Type 2 diabetes the pancreas still produces insulin but the body's cells do not respond to it properly, so oral medications that stimulate insulin production or improve insulin sensitivity are often sufficient.",
        "type": "reasoning"
    },
    {
        "user_input": "How does poor blood sugar control lead to kidney failure in diabetic patients?",
        "reference": "Persistently high blood glucose damages the small blood vessels in the kidneys over time, impairing their ability to filter waste from the blood. This progressive damage can eventually lead to renal failure.",
        "type": "reasoning"
    },
    {
        "user_input": "Why might metformin be inappropriate for certain patients?",
        "reference": "Metformin may be inappropriate for patients with kidney disease, liver disease, or heart failure because it can increase the risk of lactic acidosis. It is also not recommended for patients who drink alcohol heavily.",
        "type": "reasoning"
    },
    # Multi-hop
    {
        "user_input": "How do the symptoms, diagnosis, and treatment of Type 1 and Type 2 diabetes differ?",
        "reference": "Type 1 diabetes symptoms develop suddenly and include excessive thirst, frequent urination, and weight loss. It is diagnosed through blood glucose tests and treated with insulin injections. Type 2 diabetes symptoms develop gradually and may include slow wound healing and blurred vision. It is treated with dietary changes, oral medications, and sometimes insulin.",
        "type": "multi_hop"
    },
    {
        "user_input": "What is the relationship between hypoglycemia, insulin dosage, and diet in diabetic management?",
        "reference": "Too much insulin or insufficient food intake can cause blood sugar to drop too low, resulting in hypoglycemia. Diabetic patients must carefully balance insulin dosage with carbohydrate intake to maintain stable blood glucose levels and avoid hypoglycemic episodes.",
        "type": "multi_hop"
    },
    {
        "user_input": "How do complications of untreated diabetes affect multiple organ systems?",
        "reference": "Untreated diabetes damages multiple organ systems through chronically elevated blood glucose. It affects the kidneys causing renal failure, the cardiovascular system causing heart disease and stroke, the eyes causing blindness, and the nervous system causing neuropathy.",
        "type": "multi_hop"
    },
    # Conversational
    {
        "user_input": "What is metformin?",
        "reference": "Metformin is an oral medication used to treat Type 2 diabetes. It helps control blood sugar levels and is often the first medication prescribed for Type 2 diabetes.",
        "type": "conversational"
    },
    {
        "user_input": "What are its side effects?",
        "reference": "Common side effects of metformin include mild diarrhea, nausea, vomiting, and stomach cramps. Less common side effects include sore mouth and vaginal itching.",
        "type": "conversational"
    },
    {
        "user_input": "Can it be taken with insulin?",
        "reference": "Yes, metformin can be taken with insulin. In some Type 2 diabetes patients whose condition cannot be controlled with oral medication alone, combining metformin with insulin injections can help better manage blood sugar levels.",
        "type": "conversational"
    },
]