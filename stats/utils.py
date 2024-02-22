def get_line_chart_data(qs, label, x, y):
    labels = set(item[label] for item in qs)
    labels = list(labels)
    max_rounds = max([item[x] for item in qs])
    rounds = [r for r in range(1, max_rounds + 1)]
    points = []

    for item in labels:
        qs_name = [d for d in qs if d[label] == item]
        points_data = [0] * max_rounds
        
        for el in qs_name: 
            points_val = el[y]
            points_data[el[x]-1] = points_val

        for i, el in enumerate(points_data):
            if el == 0:
                points_data[i] = points_data[i-1]
            
        points.append(points_data)    
    
    print(rounds)
    print(labels)
    print(points)
    
    zipped = zip(labels, points)
    context = {'rounds': rounds,
               'labels_points': zipped}

    return context