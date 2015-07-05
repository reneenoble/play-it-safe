from math import radians, cos, sin, asin, sqrt
import csv

def read_csv(file_name, required_indexes, names):
    names = names.strip().split(",")
    file_o = open(file_name, "r")
    data_dicts = []
    csv_read = csv.reader(file_o)
    head = True
    for line in csv_read:
        if head:
            names = [i.lower() for i in names]
            print(names)
            head = False
        else:
            if all(line[i]!="" for i in required_indexes):
                data_dict = {names[i]: line[i] for i in range(len(names))}
                try:
                    float(data_dict["lat"])
                    float(data_dict["long"])
                    data_dicts.append(data_dict)
                except:
                    pass

    return data_dicts, names

def filter_in_radius(latlong, filter_locs, radius):
    """filter the list of filter_locs, so that only the ones that are with in the radius (in KMs) remain"""
    filtered = []
    for i in filter_locs:
        
        if haversine(float(latlong[1]), float(latlong[0]), float(i["long"]), float(i["lat"])) <= radius:
            filtered.append(i)
    return filtered

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r


play_file = "BallaratPlaygrounds.csv"
required = [3,8,9]
n_loc = "Area,ID,Constructed,Location,PlayType,Maintain,Site,Ward,long,lat"
locations, loc_names = read_csv(play_file, required, n_loc)

graffiti_file = "ballaratgraffitidefects.csv"
required = [6,7]
n_graf = "Asset,Defect,Date,Offensive,Site,Size,Long,Lat"
grafs, graf_names = read_csv(graffiti_file, required, n_graf)
print("grafs", type(grafs[0]))

cctv_file = "cctv.csv"
required = [4,5]
n_cctv = "Council_ID,Location,Type,Site,lat,long"
cctvs, cctv_names = read_csv(cctv_file, required, n_cctv)
print("cctv", type(cctvs[0]))

care_file = "ballaratchildcarecentres.csv"
required = [7,8]
n_care = "name,ID,address,contact_ph1,contact_ph2,email,url,lat,long"
care, care_names = read_csv(care_file, required, n_care)

edu_file = "ballarateducationfacilities.csv"
n_edu = "CouncilID,Name,Location,Service,Lat,Long"
required = [4,5]
edu, edu_names = read_csv(edu_file, required, n_edu)

#radius under consideration (km)
radius_cctv = 0.2
radius_graf = 1
radius_edu = 1

loc_out = []
loc_names.append("Graffiti")
loc_names.append("CCTV Cameras")
loc_names.append("Education and Childcare Centres")
loc_names.append("SAFETY SCORE:  ")

loc_out.append(loc_names)
cctv_range = []
graf_range = []
edu_range = []
#print(loc_out)
for l in locations:
    filter_cctv = filter_in_radius((l["lat"], l["long"]), cctvs, radius_cctv)
    filter_graf = filter_in_radius((l["lat"], l["long"]), grafs, radius_graf)
    filter_care = filter_in_radius((l["lat"], l["long"]), care, radius_edu)
    filter_edu = filter_in_radius((l["lat"], l["long"]), edu, radius_edu)
    
    cctv_range.append(len(filter_cctv))
    graf_range.append(len(filter_graf))
    edu_range.append((len(filter_edu) + len(filter_care)))

graf_range = sorted(graf_range)
cctv_range = sorted(cctv_range)
edu_range = sorted(edu_range)

graf_scores = [graf_range[len(graf_range)//3], graf_range[2*len(graf_range)//3]]
cctv_scores = [cctv_range[len(cctv_range)//3], cctv_range[2*len(cctv_range)//3]]
edu_scores = [edu_range[len(edu_range)//3], edu_range[2*len(edu_range)//3]]

for l in locations:
    filter_cctv = filter_in_radius((l["lat"], l["long"]), cctvs, radius_cctv)
    filter_graf = filter_in_radius((l["lat"], l["long"]), grafs, radius_graf)
    filter_care = filter_in_radius((l["lat"], l["long"]), care, radius_edu)
    filter_edu = filter_in_radius((l["lat"], l["long"]), edu, radius_edu)
    edu_len = len(filter_edu) + len(filter_care)

    if len(filter_cctv)< 1:
        cctv_score = 0
        c_word = "Low" 
    elif len(filter_cctv)< 3:
        cctv_score = -3
        c_word = "Medium"
    else:
        cctv_score = -4
        c_word = "High"

    if edu_len < 0:
        edu_score = -1
        e_word = "Low"
    elif edu_len< 2:
        edu_score = -2
        e_word = "Medium"
    else:
        edu_score = -3
        e_word = "High"

    if len(filter_graf)==0:
       graf_score = 0
       f_word = "None"
    elif len(filter_graf)< graf_scores[0]:
        graf_score = 3
        g_word = "Low"
    elif len(filter_graf)< graf_scores[1]:
        graf_score = 6
        g_word = "Medium"
    else:
        graf_score = 9
        g_word = "High"

    saftey_score = 3*(cctv_score + graf_score + edu_score + 5)

    #print("cctv", len(filter_cctv))
    #print("graffiti", len(filter_graf))
    l["Graffiti"]=g_word
    l["CCTV Cameras"]=c_word
    l["Education and Childcare Centres"] = e_word
    l["SAFETY SCORE:  "] = saftey_score
    print(e_word)
    loc_out.append([l[n] for n in loc_names])

csv_out = "safe_play.csv"
csv_out_o = open(csv_out, "w")
csvwritter = csv.writer(csv_out_o)

csvwritter.writerows(loc_out)

csv_out_o.close()
print(cctv_scores)
print(edu_scores)
print(graf_scores)



