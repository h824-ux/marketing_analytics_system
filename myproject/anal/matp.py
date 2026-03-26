import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend for saving plots
import matplotlib.pyplot as plt
import seaborn as sns
from django.conf import settings
from .models import Dataset
from django.contrib import messages  # Import messages framework


'''
Datasets must have the following variables:
0 Product name
V1 Categories      Product Category    product_category()  bar
V2(Needs fix) Price           Product Price       product_price()     boxplot
V3 Purchase date   Purchase Date       purchase_date()     bar (unusal season trends?)
V4 Customer age    Customer Age        customer_age()      grouped age, circle/bar
V5 Customer gender Gender              gender()            circle/donut                  (Optional)
1v2 Follow-up, histogram? grouped price, donut
V1v3 Follow-up, sales per month, grouped product price
V1v5 Follow-up, Categories by gender, donut
V4v1 Follow-up, Stacked bar chart, grouped age, by one category
V4v2.1 Scattered chart
V4v2.2 Follow-up, donut, grouped age, by one category, price by group
V4v3 Follow-up, bar, grouped age, and month
V2v3 Follow-up, bar, grouped price, each month
V2v5 Follow-up, scattered chart, grouped gender
3v5 Follow-up, donut, month by gender
+1 List product name, heads
-add correlation graph of related comparisons
-Category to gender
-Category to age group
-Price by age
-Price by month

More box-plot may needed

Initial: 6
Follow-up: 9
'''

def test_variables(dataset_id=None):
    try:
        # Get specific dataset or latest if no ID provided
        if dataset_id:
            dataset = Dataset.objects.get(id=dataset_id)
        else:
            dataset = Dataset.objects.latest('upload_date', 'upload_time')

        # Check if the dataset is valid
        if not use_dataset(dataset):
            return False
        
        # Proceed to run the analysis
        return True
        
    except Dataset.DoesNotExist:
        print(f'Dataset {"with ID " + str(dataset_id) if dataset_id else ""} not found')
        return False
    except pd.errors.EmptyDataError:
        print('The dataset is empty.')
        return False
    except Exception as e:
        print(f'Error processing dataset: {str(e)}')
        return False

def use_dataset(dataset, request):
    # Construct the file path using settings.MEDIA_ROOT
    file_path = os.path.join(settings.MEDIA_ROOT, 'datasets', f'{dataset.dataset_name}.csv') 
    # os.path.join: a function in the os module that connects one or more path components
    # os: a built-in os module with methods for interacting with the operating system
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f'Dataset file not found at: {file_path}')
        return False
    
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Required columns
    required_columns = ['Product Category', 'Product Price', 'Purchase Date', 'Customer Age', 'Gender']
    
    # Check columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        messages.error(request, f'Missing columns in dataset {dataset.dataset_name}: {", ".join(missing_columns)}')  # Error message
        return False
    return run_python_code(dataset)

def run_python_code(dataset):
    try:
        file_path = os.path.join(settings.MEDIA_ROOT, 'datasets', f'{dataset.dataset_name}.csv')
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
            
        # Read CSV file
        df = pd.read_csv(file_path)

        # If you expect 'Product Price' to be numeric:
        df['Product Price'] = pd.to_numeric(df['Product Price'], errors='coerce')

        df[['year', 'month', 'day']] = df['Purchase Date'].str.split("-", n=2, expand=True)

        # Convert year to numeric and check for invalid years
        df['year_num'] = pd.to_numeric(df['year'], errors='coerce')
        if (df['year_num'] < 1000).any():
            df[['day', 'month', 'year']] = df['Purchase Date'].str.split("-", n=2, expand=True)
        else:
            df[['year', 'month', 'day']] = df['Purchase Date'].str.split("-", n=2, expand=True)

        month_map = {'01': 'January', '02': 'February', '03': 'March', '04': 'April',
                    '05': 'May', '06': 'June', '07': 'July', '08': 'August',
                    '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
        df['month'] = df['month'].map(month_map)
        
        # Create all groups at once
        age_bins = [16, 24, 30, 40, 50, 60, 70, float('inf')]
        age_labels = ['16-24', '24-30', '31-40', '41-50', '51-60', '60-70', '>70']
        df['age_group'] = pd.cut(df['Customer Age'], bins=age_bins, labels=age_labels, right=False)
        
        price_bins = [0, 20, 100, 200, 300, 400, 500, 1000, float('inf')]
        price_labels = ['<20', '20-100', '100-200', '200-300', '300-400', '400-500', '500-1000', '>1000']
        df['price_group'] = pd.cut(df['Product Price'], bins=price_bins, labels=price_labels, right=False)
        
        high_price_bins = [1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, float('inf')]
        high_price_labels = ['1000-1500', '1500-2000', '2000-2500', '2500-3000', '3000-4000', '4000-5000', '5000-6000', '6000-7000', '7000-8000', '8000-9000', '9000-10000', '>10000']
        df['high_price_group'] = pd.cut(df['Product Price'], bins=high_price_bins, labels=high_price_labels, right=False)

        # Pre-calculate value counts for frequently used columns
        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        price_order = ['<20', '20-100', '100-200', '200-300', '300-400', '400-500', '500-1000', '>1000']
        age_order = ['16-24', '24-30', '31-40', '41-50', '51-60', '60-70', '>70']
        category_counts = df['Product Category'].value_counts()
        high_price_counts = df['high_price_group'].value_counts()
        price_counts = df['price_group'].value_counts().reindex(price_order)
        age_counts = df['age_group'].value_counts().reindex(age_order)
        gender_counts = df['Gender'].value_counts()
        
        # Create static directory once
        static_dir = os.path.join(settings.BASE_DIR, 'static')
        os.makedirs(static_dir, exist_ok=True)
        
        # 0. Basic Distribution Plots
        # 0.1 Product Category Distribution
        fig = plt.figure(figsize=(15, 8))
        category_counts.plot(kind='bar')
        plt.title('Product Category Distribution')
        plt.xlabel('Category')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.savefig(os.path.join(static_dir, 'category.png'), bbox_inches='tight')
        plt.close(fig)
        
        # 0.2 Price Distribution
        fig = plt.figure(figsize=(15, 8))
        price_counts.plot(kind='bar')
        plt.title('Price Distribution')
        plt.xlabel('Price Range')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.savefig(os.path.join(static_dir, 'price.png'), bbox_inches='tight')
        plt.close(fig)
        
        # 0.2.2 Deeper visualisation of all total purchase price over 1000
        fig = plt.figure(figsize=(15, 8))
        high_price_counts.plot(kind='bar')
        plt.title('Price Distribution')
        plt.xlabel('Price Range')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.savefig(os.path.join(static_dir, 'price-2.png'), bbox_inches='tight')
        plt.close(fig)
        
        # 0.3 Month Distribution by Year
        years_to_show = ['2021', '2022', '2023', '2024']
        
        for year in years_to_show:
            # Filter data for current year
            year_data = df[df['year'] == year]
            
            # Create new figure for each year
            fig = plt.figure(figsize=(15, 8))
            
            if not year_data.empty:
                # Get monthly counts for this year
                year_month_counts = year_data['month'].value_counts().reindex(month_order)
                
                # Create bar plot for this year
                year_month_counts.plot(kind='bar')
                plt.title(f'Monthly Distribution - {year}')
                plt.xlabel('Month')
                plt.ylabel('Count')
                plt.xticks(rotation=45)
                
                # adds a counter to each item in a list or other iterable
                # Add value labels on top of each bar
                for i, v in enumerate(year_month_counts):
                    if pd.notna(v):  # Check if value is not NaN
                        plt.text(i, v, str(int(v)), ha='center', va='bottom')
            else:
                plt.text(0.5, 0.5, f'No data available for {year}', 
                        ha='center', va='center', transform=plt.gca().transAxes)
                plt.title(f'Monthly Distribution - {year}')
            
            plt.tight_layout()
            # Save each year's plot as a separate file
            plt.savefig(os.path.join(static_dir, f'month_{year}.png'), bbox_inches='tight')
            plt.close(fig)
        
        # 0.4 Age Distribution
        fig = plt.figure(figsize=(5, 5))
        plt.pie(age_counts, labels=age_counts.index, autopct='%1.1f%%', startangle=90)
        plt.title('Age Group Distribution')
        plt.savefig(os.path.join(static_dir, 'age.png'))
        plt.close(fig)

        # 0.4.2
        fig = plt.figure(figsize=(15, 8))
        age_counts.plot(kind='bar')
        plt.title('Age Group Distribution')
        plt.xlabel('Age Group')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.savefig(os.path.join(static_dir, 'age-2.png'), bbox_inches='tight')
        plt.close(fig)
        
        # 0.5 Gender Distribution
        fig = plt.figure(figsize=(5, 5))
        plt.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=90)
        plt.title('Gender Distribution')
        plt.savefig(os.path.join(static_dir, 'gender.png'))
        plt.close(fig)
        
        # 1. Category Analysis
        # 1.2 Price by Category
        fig = plt.figure(figsize=(15, 8))
        sns.countplot(x="price_group", hue="Product Category", data=df)
        plt.title('Price Distribution by Category')
        plt.xlabel('Price Range')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.savefig(os.path.join(static_dir, '1-2.png'), bbox_inches='tight')
        plt.close(fig)

        #Crosstab
        if 'price_group' in df.columns and 'Product Category' in df.columns:
            contingency = pd.crosstab(df['Product Category'], df['price_group'])
            # Calculate percentages per column (price_group)
            percent = contingency.div(contingency.sum(axis=1), axis=0) * 100
            # Create annotation labels: "count\nxx%"
            annot = contingency.astype(str) + "\n" + percent.round(1).astype(str) + "%"
            fig = plt.figure(figsize=(8, 6))
            sns.heatmap(contingency, annot=annot, fmt='', cmap='Blues')
            plt.title('Count Heatmap: Product Category vs Price Group')
            plt.xlabel('Price Group')
            plt.ylabel('Product Category')
            plt.tight_layout()
            plt.savefig(os.path.join(static_dir, 'corr-1-2.png'), bbox_inches='tight')
            plt.close(fig)

        # 1.3 Category by Month
        for year in years_to_show:
            # Filter data for current year
            year_data = df[df['year'] == year]
            
            fig = plt.figure(figsize=(15, 8))
            
            if not year_data.empty:
                # Get monthly counts for this year with proper ordering
                year_month_counts = year_data.groupby(['month', 'Product Category'], observed=False).size().unstack(fill_value=0)
                year_month_counts = year_month_counts.reindex(month_order)
                
                # Create bar plot using the counts
                year_month_counts.plot(kind='bar', stacked=False, ax=plt.gca())
                plt.title(f'Monthly Distribution by Category - {year}')
                plt.xlabel('Month')
                plt.ylabel('Count')
                plt.xticks(rotation=45)
                plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
                plt.subplots_adjust(right=0.8)
                
            else:
                plt.text(0.5, 0.5, f'No data available for {year}', 
                        ha='center', va='center', transform=plt.gca().transAxes)
                plt.title(f'Monthly Distribution by Category - {year}')
            
            plt.tight_layout()
            plt.savefig(os.path.join(static_dir, f'1-3_{year}.png'), bbox_inches='tight')
            plt.close(fig)

            if 'Product Category' in df.columns and 'month' in df.columns:
                fig = plt.figure(figsize=(8, 6))

                if not year_data.empty:
                # Get monthly counts for this year with proper ordering
                    year_month_counts = year_data.groupby(['month', 'Product Category'], observed=False).size().unstack(fill_value=0)
                    year_month_counts = year_month_counts.reindex(month_order)

                    # Calculate percentages per column (price_group)
                    percent = year_month_counts.div(year_month_counts.sum(axis=1), axis=0) * 100
                    # Create annotation labels: "count\nxx%"
                    annot = year_month_counts.astype(str) + "\n" + percent.round(1).astype(str) + "%"

                    sns.heatmap(year_month_counts, annot=annot, fmt='', cmap='Blues') #Corr
                    plt.title(f'Count Heatmap: Month vs Product Category - {year}')
                    plt.xlabel('Product Category')
                    plt.ylabel('Month')
                    
                else:
                    plt.text(0.5, 0.5, f'No data available for {year}', 
                            ha='center', va='center', transform=plt.gca().transAxes)
                    plt.title(f'Count Heatmap: Month vs Product Category - {year}')

                plt.tight_layout()
                plt.savefig(os.path.join(static_dir, f'corr-1-3_{year}.png'), bbox_inches='tight')
                plt.close(fig)

        # 1.4 Category by Age
        fig = plt.figure(figsize=(15, 8))
        sns.countplot(x="age_group", hue="Product Category", data=df)
        plt.title('Category Distribution by Age')
        plt.xlabel('Age Group')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.savefig(os.path.join(static_dir, '1-4.png'), bbox_inches='tight')
        plt.close(fig)

        #Crosstab
        if 'age_group' in df.columns and 'Product Category' in df.columns:
            contingency = pd.crosstab(df['Product Category'], df['age_group'])
            # Calculate percentages per column (price_group)
            percent = contingency.div(contingency.sum(axis=1), axis=0) * 100
            # Create annotation labels: "count\nxx%"
            annot = contingency.astype(str) + "\n" + percent.round(1).astype(str) + "%"
            fig = plt.figure(figsize=(8, 6))
            sns.heatmap(contingency, annot=annot, fmt='', cmap='Blues')
            plt.title('Count Heatmap: Product Category vs Age Group')
            plt.xlabel('Age Group')
            plt.ylabel('Product Category')
            plt.tight_layout()
            plt.savefig(os.path.join(static_dir, 'corr-1-4.png'), bbox_inches='tight')
            plt.close(fig)
        
        # 1.5 Category by Gender
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
        
        # Male
        male_categories = df[df['Gender'] == 'Male']['Product Category'].value_counts()
        ax1.pie(male_categories, labels=male_categories.index, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Male Customers')
        
        # Female
        female_categories = df[df['Gender'] == 'Female']['Product Category'].value_counts()
        ax2.pie(female_categories, labels=female_categories.index, autopct='%1.1f%%', startangle=90)
        ax2.set_title('Female Customers')

        # Adjust layout and save
        plt.tight_layout()
        plt.savefig(os.path.join(static_dir, '1-5.png'))
        plt.close(fig)

        #Crosstab
        if 'Gender' in df.columns and 'Product Category' in df.columns:
            contingency = pd.crosstab(df['Product Category'], df['Gender'])
            # Calculate percentages per column (price_group)
            percent = contingency.div(contingency.sum(axis=1), axis=0) * 100
            # Create annotation labels: "count\nxx%"
            annot = contingency.astype(str) + "\n" + percent.round(1).astype(str) + "%"
            fig = plt.figure(figsize=(8, 6))
            sns.heatmap(contingency, annot=annot, fmt='', cmap='Blues')
            plt.title('Count Heatmap: Product Category vs Gender')
            plt.xlabel('Gender')
            plt.ylabel('Product Category')
            plt.tight_layout()
            plt.savefig(os.path.join(static_dir, 'corr-1-5.png'), bbox_inches='tight')
            plt.close(fig)
        
        # 2. Price Analysis
        # 2.3 Price by Month
        for year in years_to_show:
            # Filter data for current year
            year_data = df[df['year'] == year]
            
            fig = plt.figure(figsize=(15, 8))
            
            if not year_data.empty:
                # Get monthly counts for this year with proper ordering
                year_month_counts = year_data.groupby(['month', 'price_group'], observed=False).size().unstack(fill_value=0)
                year_month_counts = year_month_counts.reindex(month_order)
                
                # Create bar plot using the counts
                year_month_counts.plot(kind='bar', stacked=False, ax=plt.gca())
                plt.title(f'Monthly Distribution by Price - {year}')
                plt.xlabel('Month')
                plt.ylabel('Count')
                plt.xticks(rotation=45)
                plt.legend(title='Price', bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
                plt.subplots_adjust(right=0.8)
                
            else:
                plt.text(0.5, 0.5, f'No data available for {year}', 
                        ha='center', va='center', transform=plt.gca().transAxes)
                plt.title(f'Monthly Distribution by Price - {year}')
            
            plt.tight_layout()
            plt.savefig(os.path.join(static_dir, f'2-3_{year}.png'), bbox_inches='tight')
            plt.close(fig)

            if 'price_group' in df.columns and 'month' in df.columns:
                fig = plt.figure(figsize=(8, 6))

                if not year_data.empty:
                # Get monthly counts for this year with proper ordering
                    year_month_counts = year_data.groupby(['month', 'price_group'], observed=False).size().unstack(fill_value=0)
                    year_month_counts = year_month_counts.reindex(month_order)

                    # Calculate percentages per column (price_group)
                    percent = year_month_counts.div(year_month_counts.sum(axis=1), axis=0) * 100
                    # Create annotation labels: "count\nxx%"
                    annot = year_month_counts.astype(str) + "\n" + percent.round(1).astype(str) + "%"

                    sns.heatmap(year_month_counts, annot=annot, fmt='', cmap='Blues') #Corr
                    plt.title(f'Count Heatmap: Month vs Price Group - {year}')
                    plt.xlabel('Price Group')
                    plt.ylabel('Month')
                    
                else:
                    plt.text(0.5, 0.5, f'No data available for {year}', 
                            ha='center', va='center', transform=plt.gca().transAxes)
                    plt.title(f'Count Heatmap: Month vs Price Group - {year}')

                plt.tight_layout()
                plt.savefig(os.path.join(static_dir, f'corr-2-3_{year}.png'), bbox_inches='tight')
                plt.close(fig)   

        # 2.4 Price by Age
        fig = plt.figure(figsize=(15, 8))
        sns.countplot(x="age_group", hue="price_group", data=df)
        plt.title('Price Distribution by Age')
        plt.xlabel('Age Group')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.legend(title='Price Range', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.savefig(os.path.join(static_dir, '2-4.png'), bbox_inches='tight')
        plt.close(fig)

        #Crosstab
        if 'price_group' in df.columns and 'age_group' in df.columns:
            contingency = pd.crosstab(df['age_group'], df['price_group'])
            # Calculate percentages per column (price_group)
            percent = contingency.div(contingency.sum(axis=1), axis=0) * 100
            # Create annotation labels: -> "count\nxx%"
            annot = contingency.astype(str) + "\n" + percent.round(1).astype(str) + "%"
            fig = plt.figure(figsize=(8, 6))
            sns.heatmap(contingency, annot=annot, fmt='', cmap='Blues')
            plt.title('Count Heatmap: Age Group vs Price Group')
            plt.xlabel('Price Group')
            plt.ylabel('Age Group')
            plt.tight_layout()
            plt.savefig(os.path.join(static_dir, 'corr-2-4.png'), bbox_inches='tight')
            plt.close(fig)
        
        # 2.5 Price by Gender
        fig = plt.figure(figsize=(15, 8))
        sns.countplot(x="price_group", hue="Gender", data=df)
        plt.title('Price Distribution by Gender')
        plt.xlabel('Price Range')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.legend(title='Gender', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.savefig(os.path.join(static_dir, '2-5.png'), bbox_inches='tight')
        plt.close(fig)

        #Crosstab
        if 'Gender' in df.columns and 'price_group' in df.columns:
            contingency = pd.crosstab(df['price_group'], df['Gender'])
            # Calculate percentages per column (price_group)
            percent = contingency.div(contingency.sum(axis=1), axis=0) * 100
            # Create annotation labels: "count\nxx%"
            annot = contingency.astype(str) + "\n" + percent.round(1).astype(str) + "%"
            fig = plt.figure(figsize=(8, 6))
            sns.heatmap(contingency, annot=annot, fmt='', cmap='Blues')
            plt.title('Count Heatmap: Gender vs Price Group')
            plt.xlabel('Gender')
            plt.ylabel('Price Group')
            plt.tight_layout()
            plt.savefig(os.path.join(static_dir, 'corr-2-5.png'), bbox_inches='tight')
            plt.close(fig)
        
        # 3. Month Analysis
        # 3.4 Age by Month
        for year in years_to_show:
            # Filter data for current year
            year_data = df[df['year'] == year]
            
            fig = plt.figure(figsize=(15, 8))
            
            if not year_data.empty:
                # Get monthly counts for this year with proper ordering
                year_month_counts = year_data.groupby(['month', 'age_group'], observed=False).size().unstack(fill_value=0)
                year_month_counts = year_month_counts.reindex(month_order)
                
                # Create bar plot using the counts
                year_month_counts.plot(kind='bar', stacked=False, ax=plt.gca())
                plt.title(f'Monthly Distribution by Age - {year}')
                plt.xlabel('Month')
                plt.ylabel('Count')
                plt.xticks(rotation=45)
                plt.legend(title='Age', bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
                plt.subplots_adjust(right=0.8)
                
            else:
                plt.text(0.5, 0.5, f'No data available for {year}', 
                        ha='center', va='center', transform=plt.gca().transAxes)
                plt.title(f'Monthly Distribution by Age - {year}')
            
            plt.tight_layout()
            plt.savefig(os.path.join(static_dir, f'3-4_{year}.png'), bbox_inches='tight')
            plt.close(fig)

            if 'age_group' in df.columns and 'month' in df.columns:
                fig = plt.figure(figsize=(8, 6))

                if not year_data.empty:
                # Get monthly counts for this year with proper ordering
                    year_month_counts = year_data.groupby(['month', 'age_group'], observed=False).size().unstack(fill_value=0)
                    year_month_counts = year_month_counts.reindex(month_order)

                    # Calculate percentages per column (price_group)
                    percent = year_month_counts.div(year_month_counts.sum(axis=1), axis=0) * 100
                    # Create annotation labels: "count\nxx%"
                    annot = year_month_counts.astype(str) + "\n" + percent.round(1).astype(str) + "%"

                    sns.heatmap(year_month_counts, annot=annot, fmt='', cmap='Blues') #Corr
                    plt.title(f'Count Heatmap: Month vs Age Group - {year}')
                    plt.xlabel('Age Group')
                    plt.ylabel('Month')
                    
                else:
                    plt.text(0.5, 0.5, f'No data available for {year}', 
                            ha='center', va='center', transform=plt.gca().transAxes)
                    plt.title(f'Count Heatmap: Month vs Age Group - {year}')

                plt.tight_layout()
                plt.savefig(os.path.join(static_dir, f'corr-3-4_{year}.png'), bbox_inches='tight')
                plt.close(fig)
                
        # 3.5 Gender by Month
        for year in years_to_show:
            # Filter data for current year
            year_data = df[df['year'] == year]
            
            fig = plt.figure(figsize=(15, 8))
            
            if not year_data.empty:
                # Get monthly counts for this year with proper ordering
                year_month_counts = year_data.groupby(['month', 'Gender'], observed=False).size().unstack(fill_value=0)
                year_month_counts = year_month_counts.reindex(month_order)
                
                # Create bar plot using the counts
                year_month_counts.plot(kind='bar', stacked=False, ax=plt.gca())
                plt.title(f'Monthly Distribution by Gender - {year}')
                plt.xlabel('Month')
                plt.ylabel('Count')
                plt.xticks(rotation=45)
                plt.legend(title='Gender', bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
                plt.subplots_adjust(right=0.8)
                
            else:
                plt.text(0.5, 0.5, f'No data available for {year}', 
                        ha='center', va='center', transform=plt.gca().transAxes)
                plt.title(f'Monthly Distribution by Gender - {year}')
            
            plt.tight_layout()
            plt.savefig(os.path.join(static_dir, f'3-5_{year}.png'), bbox_inches='tight')
            plt.close(fig)

            if 'Gender' in df.columns and 'month' in df.columns:
                fig = plt.figure(figsize=(8, 6))

                if not year_data.empty:
                # Get monthly counts for this year with proper ordering
                    year_month_counts = year_data.groupby(['month', 'Gender'], observed=False).size().unstack(fill_value=0)
                    year_month_counts = year_month_counts.reindex(month_order)

                    # Calculate percentages per column (price_group)
                    percent = year_month_counts.div(year_month_counts.sum(axis=1), axis=0) * 100
                    # Create annotation labels: "count\nxx%"
                    annot = year_month_counts.astype(str) + "\n" + percent.round(1).astype(str) + "%"

                    sns.heatmap(year_month_counts, annot=annot, fmt='', cmap='Blues') #Corr
                    plt.title(f'Count Heatmap: Month vs Gender - {year}')
                    plt.xlabel('Gender')
                    plt.ylabel('Month')
                    
                else:
                    plt.text(0.5, 0.5, f'No data available for {year}', 
                            ha='center', va='center', transform=plt.gca().transAxes)
                    plt.title(f'Count Heatmap: Month vs Gender - {year}')

                plt.tight_layout()
                plt.savefig(os.path.join(static_dir, f'corr-3-5_{year}.png'), bbox_inches='tight')
                plt.close(fig)
        
        return True
                
    except Exception as e:
        print(f'Error in run_python_code: {str(e)}')
        return False

