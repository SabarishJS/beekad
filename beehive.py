import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def short_zone_x_axis(height_x):
    if height_x >= old_reg_start_ss_x and height_x <= old_reg_end_ss_x:
        return (((reg_end_ss_x - reg_start_ss_x) / (old_reg_end_ss_x - old_reg_start_ss_x)) * (height_x - old_reg_start_ss_x)) + reg_start_ss_x
    else:
        return None

def short_zone_y_axis(height_y):
    if height_y >= old_reg_start_ss_y and height_y <= old_reg_stump_height_ss_y:
        return (((reg_stump_height_ss_y - reg_start_ss_y) / (old_reg_stump_height_ss_y - old_reg_start_ss_y)) * (height_y - old_reg_start_ss_y)) + reg_start_ss_y
    elif height_y > old_reg_stump_height_ss_y and height_y <= old_reg_stump_line_ss_y:
        return (((reg_stump_line_ss_y - reg_stump_height_ss_y) / (old_reg_stump_line_ss_y - old_reg_stump_height_ss_y)) * (height_y - old_reg_stump_height_ss_y)) + reg_stump_height_ss_y
    elif height_y > old_reg_stump_line_ss_y and height_y <= old_reg_end_ss_y:
        return (((reg_end_ss_y - reg_stump_line_ss_y) / (old_reg_end_ss_y - old_reg_stump_line_ss_y)) * (height_y - old_reg_stump_line_ss_y)) + reg_stump_line_ss_y
    else:
        return None

def plot_balls(x, y, batting_type, ball_type, ax):
    x_axis_value_new = short_zone_x_axis(x)
    y_axis_value_new = short_zone_y_axis(y)
    if x_axis_value_new is not None and y_axis_value_new is not None:
        x = (x_axis_value_new / 1080 * width) - 7
        y = (y_axis_value_new / 600 * height) - 13
        color = get_ball_color(ball_type)
        ax.scatter(x, y, marker='o', color=color, label=ball_type)

def get_ball_color(ball_type):
    colors = {
        '1s': 'goldenrod',
        '2s': 'blue',
        '3s': 'green',
        '0s': 'black',
        'batwkts': 'azure',
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
    elif row['batwkts'] == 1:
        return 'batwkts'
    elif row['4s'] == 1:
        return '4s'
    elif row['6s'] == 1:
        return '6s'
    else:
        return None

# Constants
old_reg_start_ss_y = 189
old_reg_stump_height_ss_y = 312
old_reg_stump_line_ss_y = 406
old_reg_end_ss_y = 446
old_reg_start_ss_x = 144
old_reg_end_ss_x = 462
reg_start_ss_y = 90
reg_end_ss_y = 467
reg_start_ss_x = 300
reg_end_ss_x = 781
reg_stump_height_ss_y = 335
reg_stump_line_ss_y = 439
width = 0
height = 0

def main():
    st.title('Beehive Plot Generator')

    # File upload and data processing
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.write(data.head())

    # User input
    player_name_input = st.text_input("Enter the name of the player:")
    bowler_type_input = st.radio("Select bowler type:", ("Pace", "Spin", "Both"))

    if st.button("Generate Beehive Plot"):
        generate_beehive_plot(data, player_name_input, bowler_type_input)

def generate_beehive_plot(data, player_name, bowler_type):
    # Filter data based on bowler type
    if bowler_type == "Pace":
        bowler_data = data[data['PaceOrSpin'] == 1]
    elif bowler_type == "Spin":
        bowler_data = data[data['PaceOrSpin'] == 2]
    else:
        bowler_data = data

    # Check if player name is in the data
    if player_name in bowler_data['StrikerName'].unique():
        player_data = bowler_data[bowler_data['StrikerName'] == player_name]
        batting_types = player_data['battingtype'].unique()

        fig, ax = plt.subplots()
        for batting_type in batting_types:
            subset_data = player_data[player_data['battingtype'] == batting_type]
            for _, row in subset_data.iterrows():
                ball_type = determine_ball_type(row)
                if ball_type is not None:
                    plot_balls(row['x'], row['y'], row['battingtype'], ball_type, ax)

        # Show legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label='0s', markerfacecolor='black', markersize=10),
            plt.Line2D([0], [0], marker='o', color='w', label='1s', markerfacecolor='goldenrod', markersize=10),
            plt.Line2D([0], [0], marker='o', color='w', label='2s', markerfacecolor='blue', markersize=10),
            plt.Line2D([0], [0], marker='o', color='w', label='3s', markerfacecolor='green', markersize=10),
            plt.Line2D([0], [0], marker='o', color='w', label='4s', markerfacecolor='darkblue', markersize=10),
            plt.Line2D([0], [0], marker='o', color='w', label='6s', markerfacecolor='red', markersize=10),
            plt.Line2D([0], [0], marker='o', color='w', label='Wickets', markerfacecolor='azure', markersize=10),
        ]
        ax.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, 0.05), ncol=7, prop={'size':8})

        ax.set_title(f"Beehive Plot for {player_name}")

        st.pyplot(fig)
    else:
        st.write("Player name not found in the data.")

if __name__ == "__main__":
    main()
