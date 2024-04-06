import type { RequestHandler, Handle } from '@sveltejs/kit'
import { variables } from "$lib/utils/constants";
import { encodeQueryString } from '$lib/helpers/baseHelper';

export const get: RequestHandler = async ({ request, url }) => {
    const c = url.searchParams.get('c') ?? '0';
    const q = url.searchParams.get('q') ?? '0';
    const token = request.headers.get('token') ?? null;
    const headers = { 'Content-Type': 'application/json' };
    let eParroquias = [];
    const params = {
        action: 'data',
        model: `Parroquia:canton_id=${c}`,
        q: q
    }
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    let newURL = '';
    if (params) {
        newURL = `${variables.BASE_API_URI}/model/data` + await encodeQueryString(params);
    }
    else {
        newURL = `${variables.BASE_API_URI}/model/data`
    }

    const res = await fetch(newURL, {
        method: 'GET',
        headers: headers
    });

    if (res.status >= 400) {
        return {
            status: 400,
            body: eParroquias.slice(0, 1000)
        }
    }
    if (!res.ok) {
        return {
            status: 400,
            body: eParroquias.slice(0, 1000)
        }
    }
    const response = await res.json();
    //console.log(response);
    if (response.isSuccess) {
        //console.log(response.value.data.eParroquias);
        response.data.results.forEach(element => {
            eParroquias.push({ id: element.id, name: element.name })
        });

    }
    return {
        status: 200,
        body: eParroquias.slice(0, 1000)
    }
}
