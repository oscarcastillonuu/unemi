import { addToast } from "$lib/store/toastStore";
import { variables } from "$lib/utils/constants";
import { apiPOST } from "$lib/utils/requestUtils";

export const converToAscii = (str: string) => {
	return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toUpperCase();
};

const parms_type_format_ireport = async (type: undefined) => {
	let parms = '';
	if (type != undefined) {
		parms = 'pdf'
	} else if (type.indexOf('pdf') !== -1) {
		parms = 'pdf'
	} else if (type.indexOf('docx') !== -1) {
		parms = 'docx'
	} else if (type.indexOf('xlsx') !== -1) {
		parms = 'xlsx'
	} else if (type.indexOf('csv') !== -1) {
		parms = 'csv'
	}

	return parms

}


export const action_print_ireport = async (formats: undefined, parms: object): Promise<void> => {
	const format = await parms_type_format_ireport(formats);
	const url = 'report/run';
	let data = undefined;
	parms['rt'] = format;
	//console.log(url);
	//console.log(parms);
	const [res, errors] = await apiPOST(fetch, url, parms);
	if (errors.length > 0) {
		errors.forEach((element) => {
			addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
		});
	} else {
		if (!res.isSuccess) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
		} else {
			//console.log(res);
			data = res;
		}
	}

	return await data;
};


/**
 * Encode an object as url query string parameters
 * - includes the leading "?" prefix
 * - example input — {key: "value", alpha: "beta"}
 * - example output — output "?key=value&alpha=beta"
 * - returns empty string when given an empty object
 */
export const encodeQueryString = async (params) => {
	const keys = Object.keys(params)
	return await keys.length
		? "?" + keys
			.map(key => encodeURIComponent(key)
				+ "=" + encodeURIComponent(params[key]))
			.join("&")
		: ""
}