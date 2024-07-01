import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import zipfile
import os

# Define the regions and conditions for plotting the balls
OldRegStartSS_Y = 189
OldRegStumpHeightSS_Y = 312
OldRegStumpLineSS_Y = 406
OldRegEndSS_Y = 446
OldRegStartSS_X = 144
OldRegEndSS_X = 462

RegStartSS_Y = 90
RegEndSS_Y = 467
RegStartSS_X = 300
RegEndSS_X = 781
RegStumpHeightSS_Y = 335
RegStumpLineSS_Y = 439

width = 0
height = 0

def ShortZoneXaxis(HeightX):
    if HeightX >= OldRegStartSS_X and HeightX <= OldRegEndSS_X:
        return (((RegEndSS_X - RegStartSS_X) / (OldRegEndSS_X - OldRegStartSS_X)) * (HeightX - OldRegStartSS_X)) + RegStartSS_X
    else:
        return None

def ShortZoneYaxis(HeightY):
    if HeightY >= OldRegStartSS_Y and HeightY <= OldRegStumpHeightSS_Y:
        return (((RegStumpHeightSS_Y - RegStartSS_Y) / (OldRegStumpHeightSS_Y - OldRegStartSS_Y)) * (HeightY - OldRegStartSS_Y)) + RegStartSS_Y
    elif HeightY > OldRegStumpHeightSS_Y and HeightY <= OldRegStumpLineSS_Y:
        return (((RegStumpLineSS_Y - RegStumpHeightSS_Y) / (OldRegStumpLineSS_Y - OldRegStumpHeightSS_Y)) * (HeightY - OldRegStumpHeightSS_Y)) + RegStumpHeightSS_Y
    elif HeightY > OldRegStumpLineSS_Y and HeightY <= OldRegEndSS_Y:
        return (((RegEndSS_Y - RegStumpLineSS_Y) / (OldRegEndSS_Y - OldRegStumpLineSS_Y)) * (HeightY - OldRegStumpLineSS_Y)) + RegStumpLineSS_Y
    else:
        return None

def plot_balls(x, y, StrikerBattingType, ball_type):
    XAxisValue_New = ShortZoneXaxis(x)
    YAxisValue_New = ShortZoneYaxis(y)
    if XAxisValue_New is not None and YAxisValue_New is not None:
        X = (XAxisValue_New / 1080 * width) - 7
        Y = (YAxisValue_New / 600 * height) - 13
        color = get_ball_color(ball_type)
        plt.scatter(X, Y, marker='o', color=color, label=ball_type)

def get_ball_color(ball_type):
    colors = {
        '1s': 'goldenrod',
        '2s': 'blue',
        '3s': 'green',
        '0s': 'black',
        'Batwkts': 'azure',
        '4s': 'darkblue',
        '6s': 'red'
    }
    return colors.get(ball_type, 'gray')  # Default color for unknown types

def determine_ball_type(row):
    if row['1s'] == 1:
        return '1s'
    elif row['2s'] == 1:
        return '2s'
    elif row['3s'] == 1:
        return '3s'
    elif row['0s'] == 1:
        return '0s'
    elif row['Batwkts'] == 1:
        return 'Batwkts'
    elif row['4s'] == 1:
        return '4s'
    elif row['6s'] == 1:
        return '6s'
    else:
        return None

def filter_data_by_phase(data, phase_column, phase_value):
    if phase_value == "All":
        return data
    return data[data[phase_column] == phase_value]

image_paths = {
    '1': 'bee_r.jpg',
    '2': 'bee_l.jpg'
}

# Streamlit UI
st.title("Cricket Ball Trajectory Plotter")

# Upload CSV file
uploaded_file = st.file_uploader("Upload CSV file", type="csv")
if uploaded_file:
    data = pd.read_csv(uploaded_file)

    # Date filter
    data['Date'] = pd.to_datetime(data['date'], dayfirst=True)
    start_date = st.date_input("Start date", value=data['Date'].min())
    end_date = st.date_input("End date", value=data['Date'].max())
    
    # Convert start_date and end_date to datetime64[ns]
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    filtered_data = data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]
    st.write(f"Data after date filter: {filtered_data.shape[0]} rows")

    # Competition filter
    competitions = list(filtered_data['CompName'].unique())
    selected_competition = st.selectbox("Select competition", options=competitions)
    if selected_competition:
        filtered_data = filtered_data[filtered_data['CompName'] == selected_competition]
    st.write(f"Data after competition filter: {filtered_data.shape[0]} rows")

    # Batsman club filter
    bat_club_names = list(map(str, filtered_data['battingclubid'].unique()))
    selected_bat_club_name = st.selectbox("Select the batsman's club id", options=bat_club_names)
    if selected_bat_club_name:
        filtered_data = filtered_data[filtered_data['battingclubid'] == int(selected_bat_club_name)]
    st.write(f"Data after batsman club filter: {filtered_data.shape[0]} rows")

    # Match filter
    match_ids = ['All'] + list(map(str, filtered_data['matchid'].unique()))
    selected_match_id = st.selectbox("Select Match", options=match_ids)
    if selected_match_id != 'All':
        filtered_data = filtered_data[filtered_data['matchid'] == int(selected_match_id)]
    st.write(f"Data after match filter: {filtered_data.shape[0]} rows")

    # Batsman filter
    batsman_names = list(filtered_data['StrikerName'].unique())
    selected_batsman_names = st.multiselect("Select the batsman's names", options=batsman_names)
    if selected_batsman_names:
        filtered_data = filtered_data[filtered_data['StrikerName'].isin(selected_batsman_names)]
    st.write(f"Data after batsman filter: {filtered_data.shape[0]} rows")

    # Pace or Spin filter
    pace_or_spin = st.selectbox("Select bowler type", options=["Both", "Pace", "Spin"])
    if pace_or_spin == 'Pace':
        filtered_data = filtered_data[filtered_data['PaceorSpin'] == 1]
    elif pace_or_spin == 'Spin':
        filtered_data = filtered_data[filtered_data['PaceorSpin'] == 2]
    st.write(f"Data after pace/spin filter: {filtered_data.shape[0]} rows")

    # Bowling Type Group filter
    if pace_or_spin == 'Pace':
        bowling_type_options = ["All", "RAP", "LAP"]
        selected_bowling_types = st.multiselect("Select Bowling Type Group", options=bowling_type_options)
        if "All" not in selected_bowling_types:
            bowling_type_values = []
            if "RAP" in selected_bowling_types:
                bowling_type_values.append(1)
            if "LAP" in selected_bowling_types:
                bowling_type_values.append(2)
            filtered_data = filtered_data[filtered_data['BowlingTypeGroup'].isin(bowling_type_values)]
    elif pace_or_spin == 'Spin':
        bowling_type_options = ["All", "RAO", "SLAO", "RALB", "LAC"]
        selected_bowling_types = st.multiselect("Select Bowling Type Group", options=bowling_type_options)
        if "All" not in selected_bowling_types:
            bowling_type_values = []
            if "RAO" in selected_bowling_types:
                bowling_type_values.append(3)
            if "SLAO" in selected_bowling_types:
                bowling_type_values.append(4)
            if "RALB" in selected_bowling_types:
                bowling_type_values.append(5)
            if "LAC" in selected_bowling_types:
                bowling_type_values.append(6)
            filtered_data = filtered_data[filtered_data['BowlingTypeGroup'].isin(bowling_type_values)]
    st.write(f"Data after bowling type group filter: {filtered_data.shape[0]} rows")

    # Verify 'Phase3idStar' and 'Phase4id' columns exist before proceeding
    if 'Phase3idStar' in filtered_data.columns and 'Phase4id' in filtered_data.columns:
        # Phase selection
        phase_type = st.selectbox("Select phase type (3Phase/4Phase):", ["3Phase", "4Phase"])
        if phase_type == "3Phase":
            phase_options = ["All", 1, 2, 3]
            selected_phase = st.selectbox("Select Phase:", phase_options, index=0)
            filtered_data = filter_data_by_phase(filtered_data, 'Phase3idStar', selected_phase)
        elif phase_type == "4Phase":
            phase_options = ["All", 1, 2, 3, 4]
            selected_phase = st.selectbox("Select Phase:", phase_options, index=0)
            filtered_data = filter_data_by_phase(filtered_data, 'Phase4id', selected_phase)
    else:
        st.error("Phase columns 'Phase3idStar' or 'Phase4id' not found in the data.")
    
    st.write(f"Data after phase filter: {filtered_data.shape[0]} rows")

    # Run types filter
    run_type_columns = ['1s', '2s', '3s', '0s', 'Batwkts', '4s', '6s']
    run_types = st.multiselect("Select run types", options=run_type_columns)

    if run_types:
        conditions = [filtered_data[run_type] == 1 for run_type in run_types]
        if conditions:
            combined_condition = conditions[0]
            for condition in conditions[1:]:
                combined_condition |= condition
            filtered_data = filtered_data[combined_condition]

    st.write(f"Data after run types filter: {filtered_data.shape[0]} rows")

    # Ensure filtered_data is not empty before accessing its elements
    if not filtered_data.empty:
        # Create a directory to save the images
        os.makedirs("plots", exist_ok=True)

        zipf = zipfile.ZipFile("batsman_plots.zip", 'w', zipfile.ZIP_DEFLATED)

        for batsman_name in selected_batsman_names:
            batsman_data = filtered_data[filtered_data['StrikerName'] == batsman_name]
            if not batsman_data.empty:
                # Read the image corresponding to the batsman's batting type
                batsman_batting_type = batsman_data['StrikerBattingType'].iloc[0]
                image_path = image_paths[str(batsman_batting_type)]
                img = plt.imread(image_path)
                height, width, _ = img.shape

                fig, ax = plt.subplots()
                ax.imshow(img)
                ax.axis('off')  # Turn off the axes

                # Plot each ball in the batsman's data
                for index, row in batsman_data.iterrows():
                    ball_type = determine_ball_type(row)
                    if ball_type:
                        plot_balls(row['HeightX'], row['HeightY'], row['StrikerBattingType'], ball_type)

                plt.title(batsman_name)
                plt.savefig(f"plots/{batsman_name}.png")
                plt.close(fig)

                # Add the image to the zip file
                zipf.write(f"plots/{batsman_name}.png", arcname=f"{batsman_name}.png")

        zipf.close()

        # Provide download link for the zip file
        with open("batsman_plots.zip", "rb") as f:
            st.download_button("Download all plots as ZIP", f, "batsman_plots.zip")

        # Display preview of the images
        st.write("Preview of the plots:")
        for batsman_name in selected_batsman_names:
            batsman_data = filtered_data[filtered_data['StrikerName'] == batsman_name]
            if not batsman_data.empty:
                st.image(f"plots/{batsman_name}.png", caption=batsman_name)
    else:
        st.write("No data available for the selected filters.")
