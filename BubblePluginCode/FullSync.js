// Last updated: October 6, 2023
async function(properties, context) {
    const axios = require("axios").default
    let app_version = properties.one_record._call_metadata.app_version;

    // Create the request body
    let requestBody = {
        app_version: app_version,
        app_type: properties.app_type,
    }

    // Set the request headers
    let headers = {
        "x-functions-key": context.keys['Azure Key']    
    }

    try { 
        await axios.post(`${context.keys['Full Table Sync URL']}`, requestBody, {
            headers: headers,
        }) 
    } catch (error) {
    }
}