test_questions = [
    # Direct factual
    {
        "user_input": "What are Miranda rights?",
        "reference": "Miranda rights are rights that must be read to a suspect before custodial interrogation. They include the right to remain silent, the warning that anything said can be used against them in court, the right to an attorney, and the right to a court-appointed attorney if they cannot afford one.",
        "type": "direct"
    },
    {
        "user_input": "What is at-will employment?",
        "reference": "At-will employment means that an employer can terminate an employee at any time for any reason, or for no reason at all, without incurring legal liability. Similarly, an employee can quit at any time without reason. Exceptions exist for terminations based on illegal discrimination or retaliation.",
        "type": "direct"
    },
    {
        "user_input": "What is probable cause?",
        "reference": "Probable cause is a reasonable basis for believing that a crime may have been committed. It is required before law enforcement can make an arrest, conduct a search, or obtain a warrant. It is a higher standard than reasonable suspicion but lower than proof beyond a reasonable doubt.",
        "type": "direct"
    },
    {
        "user_input": "What is a security deposit?",
        "reference": "A security deposit is a sum of money paid by a tenant to a landlord before moving in, held to cover potential damages or unpaid rent. Landlords are required to return the deposit within a specified period after the tenant vacates, along with an itemized list of any deductions.",
        "type": "direct"
    },
    # Inference/reasoning
    {
        "user_input": "Why can an employer in California terminate an employee without giving a reason?",
        "reference": "California follows the at-will employment doctrine, which allows employers to terminate employees without cause or notice unless there is an employment contract, union agreement, or the termination violates anti-discrimination laws or public policy.",
        "type": "reasoning"
    },
    {
        "user_input": "Why must Miranda rights be read before interrogation and not before arrest?",
        "reference": "Miranda rights are triggered by custodial interrogation, not arrest itself. The purpose is to protect a suspect's Fifth Amendment right against self-incrimination during questioning. Statements made without Miranda warnings during custodial interrogation are generally inadmissible in court.",
        "type": "reasoning"
    },
    {
        "user_input": "Why might a landlord be required to pay punitive damages for withholding a security deposit?",
        "reference": "If a landlord willfully fails to return a security deposit or provide an itemized statement of deductions within the legally required timeframe, courts may award punitive damages to deter such conduct. The willful nature of the withholding distinguishes it from a good-faith dispute over deductions.",
        "type": "reasoning"
    },
    # Multi-hop
    {
        "user_input": "How do tenant rights regarding habitability, repairs, and rent withholding relate to each other in New York?",
        "reference": "In New York, landlords have a duty to maintain habitable conditions. If a landlord fails to make required repairs after proper notice, tenants may have remedies including rent withholding or repair-and-deduct. However, withholding rent is generally considered risky and tenants must follow proper legal procedures to avoid eviction.",
        "type": "multi_hop"
    },
    {
        "user_input": "How do the concepts of arrest, probable cause, and search and seizure interact under the Fourth Amendment?",
        "reference": "The Fourth Amendment protects against unreasonable searches and seizures and requires probable cause for arrests and search warrants. Law enforcement must have probable cause to arrest a suspect or obtain a warrant to search property. Warrantless searches are generally prohibited except under specific exceptions such as consent, plain view, or exigent circumstances.",
        "type": "multi_hop"
    },
    {
        "user_input": "How do wrongful termination, discrimination, and at-will employment interact in employment law?",
        "reference": "While at-will employment allows termination without cause, it does not permit termination for illegal reasons. Terminations motivated by race, gender, age, disability, or other protected characteristics violate anti-discrimination laws and constitute wrongful termination. Employees in at-will states can still bring wrongful termination claims if they can show the termination was discriminatory or retaliatory.",
        "type": "multi_hop"
    },
    # Conversational
    {
        "user_input": "What is the Fourth Amendment?",
        "reference": "The Fourth Amendment to the US Constitution protects citizens against unreasonable searches and seizures by the government. It requires that warrants be issued only upon probable cause, supported by oath or affirmation, and must describe the place to be searched and the persons or things to be seized.",
        "type": "conversational"
    },
    {
        "user_input": "Does it apply to private employers?",
        "reference": "No, the Fourth Amendment only protects against government action. Private employers are generally not bound by the Fourth Amendment, though they may be subject to state privacy laws or contractual obligations regarding workplace searches.",
        "type": "conversational"
    },
    {
        "user_input": "What protections do employees have against workplace searches then?",
        "reference": "Employees in the private sector may have limited protections against workplace searches under state privacy laws, employment contracts, or union agreements. Some states have enacted laws restricting employer monitoring of electronic communications or personal property searches.",
        "type": "conversational"
    },
]