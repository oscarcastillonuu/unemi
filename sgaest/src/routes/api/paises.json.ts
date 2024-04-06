import type { RequestHandler, Handle } from '@sveltejs/kit'
import { variables } from "$lib/utils/constants";
import { encodeQueryString } from '$lib/helpers/baseHelper';

export const get: RequestHandler = async ({ request, url }) => {
    const q = url.searchParams.get('q') ?? '';
    const token = request.headers.get('token') ?? null;
    const headers = { 'Content-Type': 'application/json' };
    let ePaises = [];
    const params = {
        action: 'data',
        model: 'Pais',
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
            body: ePaises.slice(0, 1000)
        }
    }
    if (!res.ok) {
        return {
            status: 400,
            body: ePaises.slice(0, 1000)
        }
    }
    const response = await res.json();
    //console.log(response);
    if (response.isSuccess) {
        //console.log(response.value.data.ePaises);
        response.data.results.forEach(element => {
            ePaises.push({ id: element.id, name: element.name })
        });

    }
    return {
        status: 200,
        body: ePaises.slice(0, 1000)
    }
}

