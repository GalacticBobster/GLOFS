import numpy as np

stations = ['APNM4', 'BUFN6', 'CNDO1', 'DBLN6', 'DULM5', 'GRMM4', 'GTLM4', 'MCYI3', 'MEEM4', 'MNMM4', 'PWAW3', 'SBLM4', 'TBIM4', 'THLO1']


for station in stations:
    station_lower = station.lower()
    fil1 = f'/glade/work/ananyo/GL/data/CMAN/{station_lower}h2024.txt' #apnm4h2024.txt 
    fil2 = f'/glade/work/ananyo/GL/data/CMAN/{station_lower}h2025.txt'
# Load both files, skipping lines that start with '#'
    data1 = np.genfromtxt(fil1, comments='#')
    data2 = np.genfromtxt(fil2, comments='#')
# Combine the arrays
    combined = np.vstack((data1, data2))

# Sort by date and time columns (YY, MM, DD, hh, mm)
    combined_sorted = combined[np.lexsort((combined[:,4], combined[:,3], combined[:,2], combined[:,1], combined[:,0]))]

# Save to a new file
    np.savetxt(f"../../CMAN/{station_lower}h20245.txt", combined_sorted, fmt="%.1f", delimiter=" ")

# Optional: Add back the header manually if needed
    header = ( "#YY  MM DD hh mm WDIR WSPD GST  WVHT   DPD   APD MWD   PRES  ATMP  WTMP  DEWP  VIS  TIDE\n" "#yr  mo dy hr mn degT m/s  m/s     m   sec   sec deg    hPa  degC  degC  degC  nmi    ft")
    print(station_lower)
    with open(f"../../CMAN/{station_lower}h20245.txt", "r+") as f:
     content = f.read()
     f.seek(0, 0)
     f.write(header + "\n" + content)

