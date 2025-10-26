# analysis_lib/axial_analysis.py

def calc_ax_prop(df, area_m2, L_m):
    """
    Calculates and adds Axial Stress and Axial Strain columns to the DataFrame.
    Assumes input DataFrame contains raw 'Force (N)' and 'Displacement (mm)'.
    """
    df_processed = df.copy()

    # Calculate Axial Stress (sigma)
    df_processed['Axial Stress (Pa)'] = df_processed['Force (N)'] / area_m2
    df_processed['Axial Stress (MPa)'] = df_processed['Axial Stress (Pa)'] / 1e6

    # Calculate Axial Strain (epsilon)
    displacement_m = df_processed['Displacement (mm)'] / 1000
    df_processed['Axial Strain'] = displacement_m / L_m

    print("Axial properties (stress and strain) calculated.")
    return df_processed