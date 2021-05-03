import requests
import datetime
import streamlit as st
import json
import pandas as pd
pd.set_option('display.max_rows', 2000)

st.title('''Get Your Vaccine availability Information''')
#for 1 time to get the csv file
# print(pd.__version__)

# district_df_all = None
# for state_code in range(1,40):
#     response = requests.get("https://cdn-api.co-vin.in/api/v2/admin/location/districts/{}".format(state_code))
#     district_df = pd.DataFrame(json.loads(response.text))
#     district_df = pd.json_normalize(district_df['districts'])
#     if district_df_all is None:
#         district_df_all = district_df
#     else:
#         district_df_all = pd.concat([district_df_all, district_df])
        
#     district_df_all.district_id = district_df_all.district_id.astype(int)
        
# district_df_all = district_df_all[["district_name", "district_id"]].sort_values("district_name")
# district_df_all.to_csv("districts.csv", index=False)

st.sidebar.title("Project Name: ")
st.sidebar.write("Vaccine availability checking")
htmlq='''<a href='https://github.com/sidharthbdash/vaccine' style='text-decoration: none;'>GitHub repo</a> '''
st.sidebar.markdown(htmlq,unsafe_allow_html=True)


age,days=st.beta_columns(2)
age=age.selectbox("Select Minimum age",(18,45))
next_n_days=days.selectbox("Select next n days",(2,3,4,5))

col_name=["district_name","district_id"]
dist_data=pd.read_csv("districts.csv",names=col_name)
d_names=dist_data.district_name.to_list()[1:]
d_ids=dist_data.district_id.to_list()[1:]

district_name=st.multiselect("Select Dist names: ",d_names)
district_ids=[]
for i in district_name:
	district_ids.append(int(d_ids[d_names.index(i)]))


if len(district_ids)>0:
	base = datetime.datetime.today()
	date_list = [base + datetime.timedelta(days=x) for x in range(next_n_days)]
	date_str = [x.strftime("%d-%m-%Y") for x in date_list]
	INP_DATE = date_str[-1]

	all_date_df = None

	for DIST_ID in district_ids:
	    print(f"checking for INP_DATE:{INP_DATE} & DIST_ID:{DIST_ID}")
	    URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={}&date={}".format(DIST_ID, INP_DATE)
	    response = requests.get(URL)
	    data = json.loads(response.text)['centers']
	    df = pd.DataFrame(data)
	    df = df.explode("sessions")
	    df['min_age_limit'] = df.sessions.apply(lambda x: x['min_age_limit'])
	    df['available_capacity'] = df.sessions.apply(lambda x: x['available_capacity'])
	    df['date'] = df.sessions.apply(lambda x: x['date'])
	    df = df[["date", "min_age_limit", "available_capacity", "pincode", "name", "state_name", "district_name", "block_name", "fee_type"]]
	    if all_date_df is not None:
	        all_date_df = pd.concat([all_date_df, df])
	    else:
	        all_date_df = df
	            
	df = df.drop(["block_name"], axis=1).sort_values(["min_age_limit", "available_capacity"], ascending=[True, False])
	if len(df[df.min_age_limit == age])==0:
		st.write("No Records Found....")
	else:
		st.write(df[df.min_age_limit == age])
		col1,col2,col3,col4=st.beta_columns(4)

		html='''<a href='https://www.cowin.gov.in/' style='text-decoration: none;'>Click here to register</a>'''
		col4.markdown(html,unsafe_allow_html=True)
