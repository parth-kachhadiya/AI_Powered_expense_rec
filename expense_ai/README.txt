expense_ai/
│
├── config/
│   └── settings.py
│
├── data/
│   └── expense.db
│
├── database/
│   ├── connection.py
│   ├── init_db.py
│   ├── category_repository.py
│   └── transaction_repository.py
│
├── engine/
│   └── expense_engine.py
│
└── main.py

1. Database repository
    a. connection.py
        Responsibilities
            1. Open connection
            2. Enable foreignkey
            3. Set row_factory
    b. init_db.py
        Responsibilities
            1. Create table if not exists
            2. Seed predefined categories
            3. Only run once

    c. Repository layer (2 files)
        
        a. category_repository.py
            Responsibilities
                1. Data retrieval Only
        b. transaction_repository.py
            Responsibilities
                1. Insert
                2. Update
                3. Soft delete
                4. Fetch

            No business rulse
            No validation
            No normalization

            Pure SQL operations only

            ⚠️ Repository layer should:
                Accept clean data   
                Return clean data
                Not modify business meaning
