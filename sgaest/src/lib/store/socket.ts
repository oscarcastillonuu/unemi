import { writable } from "svelte/store";
import { variables } from '$lib/utils/constants';
import { browserGet } from "$lib/utils/requestUtils";
import { encodeQueryString } from "$lib/helpers/baseHelper";

type State = {
  requests: Array<Request>;
};

export const stateWS = writable<State>({
  requests: [],
});

export const conectorWS = writable<WebSocket>({});
export const connect = async (params: unknown) => {
  const token = browserGet('accessToken');
  // Create a new websocket
  /*const headers: Record<string, string> = {
    // Add your custom headers here
    'Authorization': `Bearer ${token}`,
    'app': 'SGA_ESTUDIANTE',
  }
  const headerString = Object.entries(headers)
    .map(([key, value]) => `${key}: ${value}`)
    .join('\r\n');
  console.log(headerString);*/
  let endPoint = `${variables.BASE_WS}/ws/client?token=${token}&app=sge`;
  if (params) {
    endPoint = `${endPoint}` + await encodeQueryString(params);
  }
  const socket = new WebSocket(endPoint);
  socket.onopen = function (e) {
    console.log("[open] Conexión establecida");
    conectorWS.set(socket);
    //console.log("Enviando al servidor");
    /*socket.send(JSON.stringify({
      'message': "Mi nombre es John",
      'type': "demo_init"
    }));*/
  };
  socket.onmessage = function (event) {
    console.log(`[message] Datos recibidos del servidor`);
    //console.log(`[message] Datos recibidos del servidor: ${event.data}`);
    const data: Request = JSON.parse(event.data);
    stateWS.update((state_ws) => ({
      ...state_ws,
      requests: [data].concat(state_ws.requests),
    }));
  };
  socket.onclose = function (event) {
    console.log('[close] Conexión cerrada correctamente');
    /*if (event.wasClean) {
      console.log(`[close] Conexión cerrada limpiamente, código=${event.code}${event.reason != "" ? ' motivo='+event.reason  : ''}`);
    } else {
      // ej. El proceso del servidor se detuvo o la red está caída
      // event.code es usualmente 1006 en este caso
      console.log('[close] La conexión se cayó');
    }*/
  };
  socket.onerror = function (error) {
    console.log(`[error] ${error.message}`);
  };
  /*socket.addEventListener("message", (message: any) => {
    console.log("message:", message)
    // Parse the incoming message here
    const data: Request = JSON.parse(message.data);
    // Update the state.  That's literally it.  This can happen from anywhere:
    // we're not in a component, and there's no nested context.
    stateWS.update((state) => ({
      ...state,
      requests: [data].concat(state.requests),
    }));
  });*/
};