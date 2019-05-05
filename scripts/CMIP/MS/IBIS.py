from CMIP import *
class IBIS:
    # 此处unit为模型输出数据的单位
    # scale 为从模型输出单位转为metric单位的缩放因子
    daily_cols = [
        {
            "id": "iyear",
            "type": "",
            "description": "year number",
            "scale": 1.0,
            "offset": 0.0,
            "unit": "",
            "metricName": "year-number"
        }, {
            "id": "imonth",
            "type": "",
            "description": "month number",
            "scale": 1.0,
            "offset": 0.0,
            "unit": "",
            "metricName": "month-number"
        }, {
            "id": "iday",
            "type": "",
            "description": "day number",
            "scale": 1.0,
            "offset": 0.0,
            "unit": "",
            "metricName": "day-number"
        }, {
            "id": "adrain",
            "type": "",
            "description": "daily average rainfall rate",
            "scale": 1.0,
            "offset": 0.0,
            "unit": "mm d-1",
            "metricName": "daily-average-rainfall-rate"
        }, {
            "id": "adsnow",
            "type": "",
            "description": "daily average snowfall rate",
            "scale": 1.0,
            "offset": 0.0,
            "unit": "mm d-1",
            "metricName": "daily-average-snowfall-rate"
        }, {
            "id": "adaet",
            "type": "",
            "description": "daily average aet",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 5.60,
            "unit": "mm d-1",
            "metricName": "daily-average-aet"
        }, {
            "id": "adtrans",
            "type": "",
            "description": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 3.42,
            "unit": "",
            "metricName": ""
        }, {
            "id": "adinvap",
            "type": "",
            "description": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 4,
            "unit": "",
            "metricName": ""
        }, {
            "id": "adsuvap",
            "type": "",
            "description": "",
            "scale": 1,
            "offset": 0.0,
            "min": 0,
            "max": 1,
            "unit": "",
            "metricName": ""
        }, {
            "id": "adtrunoff",
            "type": "",
            "description": "daily average total runoff",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 2.4,
            "unit": "mm d-1",
            "metricName": "daily-average-total-runoff"
        }, {
            "id": "adsrunoff",
            "type": "",
            "description": "daily average surface runoff",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 2.4,
            "unit": "mm d-1",
            "metricName": "daily-average-surface-runoff"
        }, {
            "id": "addrainage",
            "type": "",
            "description": "daily average drainage",
            "scale": 1.0,
            "offset": 0.0,
            "unit": "mm d-1",
            "metricName": "daily-average-drainage"
        }, {
            "id": "adrh",
            "type": "",
            "description": "daily average relative humidity",
            "scale": 1.0,
            "offset": 0.0,
            "unit": "percent",
            "metricName": "daily-average-rh"
        }, {
            "id": "adsnod",
            "type": "",
            "description": "daily average snow depth",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.36,
            "unit": "m",
            "metricName": "daily-average-snow-depth"
        }, {
            "id": "adsnof",
            "type": "",
            "description": "daily average snow fraction",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.75,
            "unit": "fraction",
            "metricName": "daily-average-snow-fraction"
        }, {
            "id": "adwsoi",
            "type": "",
            "description": "daily average soil moisture",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.79,
            "unit": "fraction",
            "metricName": "daily-average-soil-moisture"
        }, {
            "id": "adwisoi",
            "type": "",
            "description": "daily average soil ice",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.79,
            "unit": "fraction",
            "metricName": "daily-average-soil-ice"
        }, {
            "id": "adtsoi",
            "type": "",
            "description": "daily average soil temperature",
            "scale": 1.0,
            "offset": 0.0,
            "min": 255,
            "max": 310,
            "unit": "°C",
            "metricName": "daily-average-soil-temperature"
        }, {
            "id": "adwsoic",
            "type": "",
            "description": "daily average soil moisture using root profile weighting",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.8,
            "unit": "fraction",
            "metricName": "daily-average-soil-moisture-using-root-profile-weighting"
        }, {
            "id": "adtsoic",
            "type": "",
            "description": "daily average soil temperature using profile weighting",
            "scale": 1.0,
            "offset": 0.0,
            "min": 255,
            "max": 310,
            "unit": "°C",
            "metricName": "daily-average-soil-temperature-using-profile-weighting"
        }, {
            "id": "adco2mic",
            "type": "",
            "description": "daily accumulated co2 respiration from microbes",
            "scale": 1,
            "offset": 0.0,
            "min": 0,
            "max": 0.6,
            "unit": "kgN m-2 d-1",
            "metricName": "daily-accumulated-co2-respiration-from-microbes"
        }, {
            "id": "adco2root",
            "type": "",
            "description": "daily accumulated co2 respiration from roots",
            "scale": 1,
            "offset": 0.0,
            "min": 0,
            "max": 2,
            "unit": "kgC m-2 d-1",
            "metricName": "daily-accumulated-co2-respiration-from-roots"
        }, {
            "id": "adco2soi",
            "type": "",
            "description": "daily accumulated co2 respiration from soil(total)",
            "scale": 1,
            "offset": 0.0,
            "min": 0,
            "max": 2.5,
            "unit": "kgC m-2 d-1",
            "metricName": "daily-accumulated-co2-respiration-from-soil(total)"
        }, {
            "id": "adco2ratio",
            "type": "",
            "description": "ratio of root to total co2 respiration",
            "scale": 1,
            "offset": 0.0,
            "min": 227,
            "max": 332,
            "unit": "kgC m-2 d-1",
            "metricName": "ratio-of-root-to-total-co2-respiration"
        }, {
            "id": "adnmintot",
            "type": "",
            "description": "daily accumulated net nitrogen mineralization",
            "scale": 1,
            "offset": 0.0,
            "min": 0,
            "max": 0.006,
            "unit": "kgN m-2 d-1",
            "metricName": "daily-accumulated-net-nitrogen-mineralization"
        }, {
            "id": "adtlaysoi",
            "type": "",
            "description": "daily average soil temperature of top layer",
            "scale": 1.0,
            "offset": 0.0,
            "min": 255,
            "max": 310,
            "unit": "°C",
            "metricName": "daily-average-soil-temperature-of-top-layer"
        }, {
            "id": "adwlaysoi",
            "type": "",
            "description": "daily average soil moisture of top layer",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.8,
            "unit": "fraction",
            "metricName": "daily-average-soil-moisture-of-top-layer"
        }, {
            "id": "adneetot",
            "type": "",
            "description": "daily accumulated net ecosystem exchange of co2 in ecosystem",
            "scale": 1,
            "offset": 0.0,
            "min": -0.06,
            "max": 0.08,
            "unit": "gC m-2 d-1",
            "metricName": "daily-average-NEE"
        }, {
            "id": "adgpptot",
            "type": "",
            "description": "daily average GPP",
            "scale": 1,
            "offset": 0.0,
            "min": 0,
            "max": 4.5,
            "unit": "gC m-2 d-1",
            "metricName": "daily-average-GPP"
        }, {
            "id": "adnpptot",
            "type": "",
            "description": "daily average NPP",
            "scale": 1,
            "offset": 0.0,
            "min": 0,
            "max": 1,
            "unit": "gC m-2 d-1",
            "metricName": "daily-average-NPP"
        }
    ]
    month_cols = daily_cols[3:]
    annual_cols = month_cols
    original_annual_cols = [
        {
            "id": "iyear",
            "type": "",
            "description": "year number",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            # "max": ,
            "unit": "",
            "metricName": "year-number"
        }, {
            "id": "ayprcp",
            "description": "annual average precipitation",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            # "max": ,
            "unit": "mm y-1",
            "metricName": "annual-average-precipitation"
        }, {
            "id": "ayaet",
            "description": "annual average aet",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 2000,
            "unit": "mm y-1",
            "metricName": "annual-average-aet"
        }, {
            "id": "aytrans",
            "description": "annual average transpiration",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 1251,
            "unit": "mm y-1",
            "metricName": "annual-average-transpiration"
        }, {
            "id": "ayinvap",
            "description": "",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 1500,
            "unit": ""
        }, {
            "id": "aysuvap",
            "description": "",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 360,
            "unit": ""
        }, {
            "id": "aytrunoff",
            "description": "annual average total runoff",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 492,
            "unit": "mm y-1",
            "metricName": "annual-average-total-runoff"
        }, {
            "id": "aysrunoff",
            "description": "annual average surface runoff",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": -80,
            "max": 492,
            "unit": "mm y-1",
            "metricName": "annual-average-surface-runoff"
        }, {
            "id": "aydrainage",
            "description": "annual average drainage",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            # "max": ,
            "unit": "mm y-1",
            "metricName": "annual-average-drainage"
        }, {
            "id": "aydwtot",
            "description": "annual average soil+vegetation+snow water recharge",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            # "max": ,
            "unit": "mm y-1",
            "metricName": "annual-average-soil+vegetation+snow-water-recharge"
        }, {
            "id": "aywsoi",
            "description": "annual average 1m soil moisture",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.8,
            "unit": "fraction",
            "metricName": "annual-average-1m-soil-moisture"
        }, {
            "id": "aywisoi",
            "description": "annual average 1m soil ice",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.75,
            "unit": "fraction",
            "metricName": "annual-average-1m-soil-ice"
        }, {
            "id": "ayvwc",
            "description": "annual average 1m volumetric water content",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            # "max": ,
            "unit": "fraction",
            "metricName": "annual-average-1m-volumetric-water-content"
        }, {
            "id": "ayawc",
            "description": "annual average 1m plant-available water content",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            # "max": ,
            "unit": "fraction",
            "metricName": "annual-average-1m-plant-available-water-content"
        }, {
            "id": "aytsoi",
            "description": "annual average 1m soil temperature",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 255,
            "max": 310,
            "unit": "°C",
            "metricName": "annual-average-1m-soil-temperature"
        }, {
            "id": "ayrratio",
            "description": "annual average runoff ratio",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            # "max": ,
            "unit": "fraction",
            "metricName": "annual-average-runoff-ratio"
        }, {
            "id": "aytratio",
            "description": "annual average transpiration ratio",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            # "max": ,
            "unit": "fraction",
            "metricName": "annual-average-transpiration-ratio"
        }, {
            "id": "aysolar",
            "description": "annual average incident solar radiation",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            # "max": ,
            "unit": "w m-2",
            "metricName": "annual-average-incident-solar-radiation"
        }, {
            "id": "ayalbedo",
            "description": "annual average solar albedo",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            # "max": ,
            "unit": "fraction",
            "metricName": "annual-average-solar-albedo"
        }, {
            "id": "ayirdown",
            "description": "annual average downward ir radiation",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            # "max": ,
            "unit": "w m-2",
            "metricName": "annual-average-downward-ir-radiation"
        }, {
            "id": "ayirup",
            "description": "annual average upward ir radiation",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            # "max": ,
            "unit": "w m-2",
            "metricName": "annual-average-upward-ir-radiation"
        }, {
            "id": "aysens",
            "description": "annual average sensible heat flux",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            # "max": ,
            "unit": "w m-2",
            "metricName": "annual-average-sensible-heat-flux"
        }, {
            "id": "aylatent",
            "description": "annual average latent heat flux",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            # "max": ,
            "unit": "w m-2",
            "metricName": "annual-average-latent-heat-flux"
        }, {
            "id": "aystresstu",
            "description": "annual average soil moisture stress parameter for upper canopy",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            # "max": ,
            "unit": "1",
            "metricName": "annual-average-soil-moisture-stress-parameter-for-upper-canopy"
        }, {
            "id": "aystresstl",
            "description": "annual average soil moisture stress parameter for lower canopy",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            # "max": ,
            "unit": "1",
            "metricName": "annual-average-soil-moisture-stress-parameter-for-lower-canopy"
        }, {
            "id": "ayanpptot",
            "description": "annual above-ground npp for ecosystem",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.563965,
            "unit": "kgC m-2 y-1",
            "metricName": "annual-above-ground-npp-for-ecosystem"
        }, {
            "id": "aynpptot",
            "description": "annual total npp for ecosystem",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.7,
            "unit": "kgC m-2 y-1",
            "metricName": "annual-total-npp-for-ecosystem"
        }, {
            "id": "aygpptot",
            "description": "annual total gpp for ecosystem",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 4.5,
            "unit": "kgC m-2 y-1",
            "metricName": "annual-total-gpp-for-ecosystem"
        }, {
            "id": "ayalit",
            "description": "aboveground litter",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 577179,
            "unit": "kgC m-2",
            "metricName": "aboveground-litter"
        }, {
            "id": "ayblit",
            "description": "belowground litter",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 226645,
            "unit": "kgC m-2",
            "metricName": "belowground-litter"
        }, {
            "id": "aycsoi",
            "description": "total soil carbon",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 8.63464,
            "unit": "kgC m-2",
            "metricName": "total-soil-carbon"
        }, {
            "id": "aycmic",
            "description": "total soil carbon in microbial biomass",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.086731,
            "unit": "kgC m-2",
            "metricName": "total-soil-carbon-in-microbial-biomass"
        }, {
            "id": "ayanlit",
            "description": "aboveground litter nitrogen",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.00256,
            "unit": "kgN m-2",
            "metricName": "aboveground-litter-nitrogen"
        }, {
            "id": "aybnlit",
            "description": "belowground litter nitrogen",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.0016479,
            "unit": "kgN m-2",
            "metricName": "belowground-litter-nitrogen"
        }, {
            "id": "aynsoi",
            "description": "total soil nitrogen",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.8,
            "unit": "kgN m-2",
            "metricName": "total-soil-nitrogen"
        }, {
            "id": "ynleach",
            "description": "",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.00244,
            "unit": ""
        }, {
            "id": "ayneetot",
            "description": "annual total NEE for ecosystem",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": -0.06,
            "max": 0.0064,
            "unit": "kgC m-2 y-1",
            "metricName": "annual-total-NEE-for-ecosystem"
        }, {
            "id": "ayco2mic",
            "description": "annual total CO2 flux from microbial respiration",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.621277,
            "unit": "kgC m-2 y-1",
            "metricName": "annual-total-CO2-flux-from-microbial-respiration"
        }, {
            "id": "ayco2root",
            "description": "annual total CO2 flux from soil due to root respiration",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 8000,
            "unit": "kgC m-2 y-1",
            "metricName": "annual-total-CO2-flux-from-soil-due-to-root-respiration"
        }, {
            "id": "ayco2soi",
            "description": "annual total soil CO2 flux from microbial and root respiration",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 8000,
            "unit": "kgC m-2 y-1",
            "metricName": "annual-total-soil-CO2-flux-from-microbial-and-root-respiration"
        }, {
            "id": "aynmintot",
            "description": "annual total nitrogen mineralization",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            # "max": ,
            "unit": "kgN m-2/yr",
            "metricName": "annual-total-nitrogen-mineralization"
        }, {
            "id": "ayrootbio",
            "description": "annual average live root biomass",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 1.4,
            "unit": "kgC m-2",
            "metricName": "annual-average-live-root-biomass"
        }, {
            "id": "ayclitlm",
            "description": "",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.00976562,
            "unit": ""
        }, {
            "id": "falll",
            "description": "annual leaf litter fall",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.25,
            "unit": "kgC m-2 y-1",
            "metricName": "annual-leaf-litter-fall"
        }, {
            "id": "fallr",
            "description": "annual root litter input",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.3055,
            "unit": "kgC m-2 y-1",
            "metricName": "annual-root-litter-input"
        }, {
            "id": "fallw",
            "description": "annual wood litter fall",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.28,
            "unit": "kgC m-2 y-1",
            "metricName": "annual-wood-litter-fall"
        }, {
            "id": "aylail",
            "description": "",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 5.7,
            "unit": ""
        }, {
            "id": "aylaiu",
            "description": "",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 5.2,
            "unit": ""
        }, {
            "id": "biomass(pft)",
            "description": "total biomass of each plant functional type",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 7.9,
            "unit": "kgC m-2",
            "metricName": "total-biomass-of-each-plant-functional-type"
        }, {
            "id": "cbiol(pft)",
            "description": "carbon in leaf biomass pool",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.323,
            "unit": "kgC m-2",
            "metricName": "carbon-in-leaf-biomass-pool"
        }, {
            "id": "cbiow(pft)",
            "description": "carbon in woody biomass pool",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 7,
            "unit": "kgC m-2",
            "metricName": "carbon-in-woody-biomass-pool"
        }, {
            "id": "cbior(pft)",
            "description": "carbon in fine root biomass pool",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 1.4,
            "unit": "kgC m-2",
            "metricName": "carbon-in-fine-root-biomass-pool"
        }
    ]
    lishihua_cols = [
        {
            "id": "iyear",
            "description": "annual leaf litter fall",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
        },
        {
            "id": "falll",
            "description": "annual leaf litter fall",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.25,
            "unit": "kgC m-2 y-1",
            "metricName": "annual-leaf-litter-fall"
        },
        {
            "id": "fallw",
            "description": "annual wood litter fall",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.25,
            "unit": "kgC m-2 y-1",
            "metricName": "annual-wood-litter-fall"
        },
        {
            "id": "aylail",
            "description": "",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 5.8,
            "unit": ""
        }, {
            "id": "aylaiu",
            "description": "",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 5.8,
            "unit": ""
        },
        {
            "id": "ayco2mic",
            "description": "annual total CO2 flux from microbial respiration",
            "type": "",
            "scale": 1.0,
            "offset": 0.0,
            "min": 0,
            "max": 0.7,
            "unit": "kgC m-2 y-1",
            "metricName": "annual-total-CO2-flux-from-microbial-respiration"
        }
    ]
    def __init__(self, time):
        self.time = time
        if self.time == 'lishihua':
            self.name = 'IBIS-lishihua'
        else:
            self.name = 'IBIS'

    @property
    def cols(self):
        if self.time == 'annual':
            return IBIS.annual_cols
        elif self.time == 'month':
            return IBIS.month_cols
        elif self.time == 'daily':
            return IBIS.daily_cols
        elif self.time == 'original-annual':
            return IBIS.original_annual_cols
        elif self.time == 'lishihua':
            return IBIS.lishihua_cols
    
    @property
    def to_month_usecols(self):
        return np.arange(len(IBIS.month_cols))
    
    @property
    def folder(self):
        if self.time == 'lishihua':
            return DATA_HOME + '/IBIS_Data/5b9012e4c29ca433443dcfab/lishihua/Output/correct'
        else:
            return DATA_HOME + '/IBIS_Data/5b9012e4c29ca433443dcfab/outputs'
    
    @property
    def suffix(self):
        if self.time == 'original-annual':
            return '.annual.txt'
        elif self.time == 'lishihua':
            return '.txt'
        else:
            return '.%s.txt' % self.time

    def getCol(self, metricName):
        return next(item for item in self.cols if item['metricName'] == metricName)

    def annual_max(self, feature):
        d = {
            'daily-average-GPP': 4.5,
            'daily-average-NPP': 1,
            'daily-average-NEE': 0.079
        }
        return d[feature]

    def annual_min(self, feature):
        if feature == 'daily-average-NEE':
            return -0.107
        return 0