import pandas as pd
# приводим в формат датывремя
df['time'] = pd.to_datetime(df['time'])

# 1. находим пользователей, чей первый заход в стор/регистрация (product is null) был не раньше 2024-03-01
first_null_product = (
    df[df['product'].isna()]
    .groupby('userid', as_index=False)['time']
    .min()
    .rename(columns={'time': 'first_null_product_time'})
)
eligible_users = first_null_product[first_null_product['first_null_product_time'] >= pd.Timestamp('2024-03-01')]['userid']

# 2. находим первую дату launch после 2023-03-01 для этих пользователей
first_launch = (
    df[(df['eventname'] == 'launch') &
       (df['time'] > pd.Timestamp('2023-03-01')) &
       (df['userid'].isin(eligible_users))]
    .groupby('userid', as_index=False)['time']
    .min()
    .rename(columns={'time': 'first_launch_date'})
)

# 3. находим пользователей, которые сделали хотя бы одно update в течение 14 дней после первого запуска
updates_in_14_days = []
for _, row in first_launch.iterrows():
    uid = row['userid']
    start = row['first_launch_date']
    end = start + pd.Timedelta(days=14)
    if not df[(df['userid'] == uid) &
              (df['eventname'] == 'update') &
              (df['time'] >= start) &
              (df['time'] < end)].empty:
        updates_in_14_days.append(uid)
updates_in_14_days = set(updates_in_14_days)

# 4. считаем по неделям
first_launch['week'] = first_launch['first_launch_date'].dt.isocalendar().week
result = (
    first_launch
    .groupby('week')
    .agg(
        users=('userid', 'nunique'),
        cr=('userid', lambda x: round(len(set(x) & updates_in_14_days) / len(x), 2))
    )
    .reset_index()
    .sort_values('week')
)

print(result)
