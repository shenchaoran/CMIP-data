const path = require('path')
const Bluebird = require('bluebird')
const fs = Bluebird.promisifyAll(require('fs'))
const _ = require('lodash')
let fluxnetSites = require('./FLUXNET2015-sites-db.js')
const child_process = require('child_process')

const obsFolder = 'E:/Data/CMIP/FLUXNET/LaThuile'
const distFolder = 'E:/Data/CMIP/FLUXNET/refactored'

let fn = async () => {
    let fslist = await fs.readdirAsync(obsFolder)
    let sites = []
    fslist.map(fs => {
        let group = fs.match(/^(\w+-\w+)\.(\d+)\.synth\.daily\.allvars\.csv$/)
        if (group && group.length === 3) {
            let site = _.find(sites, site => site.id === group[1])
            let year = parseInt(group[2])
            if (!site) {
                // TODO lat & long
                site = {
                    id: group[1],
                }
                sites.push(site)
                let fluxnetSite = _.find(fluxnetSites, site => site.SITE_ID === group[1])
                if (fluxnetSite) {
                    site.lat = parseFloat(_.get(fluxnetSite, 'GRP_LOCATION.LOCATION_LAT'))
                    site.long = parseFloat(_.get(fluxnetSite, 'GRP_LOCATION.LOCATION_LONG'))
                    site.name = _.get(fluxnetSite, 'SITE_NAME')
                    site.url = _.get(fluxnetSite, 'URL_AMERIFLUX')
                }
            }
            if (!site.startTime || site.startTime > year)
                site.startTime = year
            if (!site.endTime || site.endTime < year)
                site.endTime = year
        } else {
            return null;
        }
    }).filter(e => !!e)


    return sites;
}
const header = 'Year,DoY,NEE_f,NEE_f_delta,GPP_f,GPP_f_delta,Reco,NEE_GPP_fqcOK,LE_f,LE_fqcOK,H_f,H_fqcOK,G_f,G_fqcOK,Ta_f,Ta_fqcOK,Ts1_f,Ts1_fqcOK,Ts2_f,Ts2_fqcOK,VPD_f,VPD_fqcOK,Precip_f,Precip_fqcOK,SWC1_f,SWC1_fqcOK,SWC2_f,SWC2_fqcOK,WS_f,WS_fqcOK,Rg_f,Rg_fqcOK,PPFD_f,PPFD_fqcOK,Rn_f,Rn_fqcOK,Rg_pot,Rd,Rd_qcOK,Rr,Rr_qcOK,PPFDbc,PPFDbc_qcOK,PPFDd,PPFDd_qcOK,PPFDr,PPFDr_qcOK,FAPAR,FAPAR_qcOK,LWin,LWin_qcOK,LWout,LWout_qcOK,SWin,SWin_qcOK,SWout,SWout_qcOK,H2Ostor1,H2Ostor2,Reco_E0_100,Reco_E0_200,Reco_E0_300,wdef_cum,wbal_clim,wbal_act,Drain,NEE_mor_f,NEE_mid_f,NEE_aft_f,GPP_mor_f,GPP_mid_f,GPP_aft_f,Ecov_mor_f,Ecov_mid_f,Ecov_aft_f,gsurf_mor_f,gsurf_mid_f,gsurf_aft_f,H_mor_f,H_mid_f,H_aft_f,Tair_min_f,Tair_max_f,NEE_night_f,NEE_midnight_f,VPDday_f,EpotPT_day_viaRn,WUE_GPP,WUE_NEE,RUE_GPP,RUE_NEE,b_GPP_Ecov,b_NEE_Ecov,a_GPP_Ecov,a_NEE_Ecov,a_sig_GPP_Ecov,a_sig_NEE_Ecov,b_GPP_Rg,b_NEE_Rg,a_GPP_Rg,a_NEE_Rg,a_sig_GPP_Rg,a_sig_NEE_Rg,Precip8,Precip30,Precip60,wbal_act8,wbal_act30,wbal_act60,Epot_viaLE_H,EpotPT_viaLE_H,Epot_viaRg,Epot_viaRn,Epot_f,Epot_flag,gsurf_viaRg,gsurf_viaRn,gsurf_viaLE_H,gsurf_f,gsurf_flag,EpotPT_viaRn,H2Ostor1_hWHC,H2Ostro2_hWHC,Drain_hWHC\n'

fn()
    .then(async sites => {
        sites.map(site => {
            Bluebird.map(new Array(site.endTime - site.startTime + 1).fill(0).map((v, i) => i+site.startTime), async year => {
                let str = await fs.readFileAsync(`${obsFolder}/${site.id}.${year}.synth.daily.allvars.csv`, 'utf8')
                let a =  str.replace(/.*\r\n/, '')
                return a;
            })
                .then(async rsts => {
                    let data = header + rsts.join('')
                    await fs.writeFileAsync(`${distFolder}/${site.id}.csv`, data, 'utf8')
                })
        }, {
            concurrency: 1
        })
    })