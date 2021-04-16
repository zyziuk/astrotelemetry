

def format_measurement_to_str_influx(measure, device, field, label, value):

    if str(type(value)) == "<class 'str'>":
        quotation = "\""
    else:
        quotation = ""

    measure = measure.replace(" ","_").replace(",","_")
    device = device.replace(" ","_").replace(",","_")
    field = field.replace(" ","_").replace(",","_")
    label = label.replace(" ","_").replace(",","_")
    value = str(value).replace(" ","_").replace(",","_")

    data = measure+",astro_device="+device+" "+field+"("+label+")"+"="+quotation+value+quotation
    
    return data.upper()
