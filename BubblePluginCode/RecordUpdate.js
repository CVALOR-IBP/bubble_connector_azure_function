// Last updated: October 6, 2023
async function(properties, context) {
    const axios = require("axios").default
    let app_version = properties.record_before._call_metadata.app_version

    // Get record ID and action
    let rb_id = await properties.record_before.get("_id");
    let ra_id = await properties.record_after.get("_id");
    let record_id = "";
    let record_action = "";
    
    if (rb_id === null) {
    	record_action = "INSERT";
        record_id = ra_id;
    } else if (ra_id === null) {
    	record_action = "DELETE";
        record_id = rb_id;
    } else {
    	record_action = "UPDATE";
        record_id = ra_id;
    }
    
    let requestBody = {
        app_version: app_version,
    	app_type: properties.app_type,
        record_id: record_id,
        record_action: record_action,
    }
    
    let headers = {
        "x-functions-key": context.keys['Azure Key']    
    }
    
    try { 
        let resp = await axios.post(`${context.keys['Record Update Function URL']}`, requestBody, {
            headers: headers
        })
        return {
        	needs_sync: resp.data.needs_full_sync
        }
    } catch (error) {
        return {
        	needs_sync: false
        }
    }
    
}