import type { RequestHandler, Handle } from '@sveltejs/kit'
import { variables } from "$lib/utils/constants";
import { encodeQueryString } from '$lib/helpers/baseHelper';

export const get: RequestHandler = async ({ request, url }) => {
    const q = url.searchParams.get('q') ?? '';
    const s = url.searchParams.get('s') ?? '0';
    const token = request.headers.get('token') ?? null;
    const headers = { 'Content-Type': 'application/json' };
    let eSubAreas = [];
    const params = {
        action: 'data',
        model: `SubAreaEspecificaConocimientoTitulacion:areaconocimiento_id=${s}`,
        q: q,
        limit: 100
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
            body: eSubAreas.slice(0, 1000)
        }
    }
    if (!res.ok) {
        return {
            status: 400,
            body: eSubAreas.slice(0, 1000)
        }
    }
    const response = await res.json();
    //console.log(response);
    if (response.isSuccess) {
        //console.log(response.value.data.eSubAreas);
        response.data.results.forEach(element => {
            eSubAreas.push({ id: element.id, name: element.name })
        });

    }
    return {
        status: 200,
        body: eSubAreas.slice(0, 1000)
    }
}

