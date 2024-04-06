<script lang="ts">
	import { onMount } from 'svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';
    export let aData;
	let asistencia = [];
    let nombres = '';
	onMount(async () => {
		asistencia = aData.detalle_leccion;
        nombres = aData.nombres;


	});
</script>

<div class="card-body">
	<div class="text-center">
		<b>{nombres}</b>
	<br>
	<br>
	</div>
	<div class="table-responsive">
		<table class="table table-sm mb-0 text-nowrap table-border table-hover">
			<thead class="table-light">
				<tr>
					<th scope="col" class="border-top-0 text-center align-middle">Nº</th
					>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 15rem;">Fecha</th>
                    <th scope="col" class="border-top-0 text-center align-middle " style="width: 15rem;">Hora</th>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 15rem;">IP</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Navegador</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Sistema Operativo</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Tamaño de la pantalla</th>

				</tr>
			</thead>
			<tbody>
                {#if asistencia}

                    {#if asistencia.length > 0}
                        {#each asistencia as asist, i}
						<tr>
                        <td  class="fs-8 align-middle border-top-0 text-center text-wrap"> { i + 1}</td>
                        <td class="fs-8 align-middle border-top-0 text-center text-wrap">{asist.fecha}</td>
                        <td class="fs-8 align-middle border-top-0 text-center text-wrap">{asist.hora}</td>
                        <td class="fs-8 align-middle border-top-0 text-center text-wrap">{asist.ip_public} </td>
                        <td class="fs-8 align-middle border-top-0 text-center text-wrap">{asist.browser}</td>
                        <td class="fs-8 align-middle border-top-0 text-center text-wrap">{asist.ops} </td>
                        <td class="fs-8 align-middle border-top-0 text-center text-wrap">{asist.screen_size}</td>
					</tr>
                        {/each}
                    {:else}
                        <tr>
                            <td colspan="8" class="text-center">NO EXISTE DETALLE DE ASISTENCIA</td>
                        </tr>
                    {/if}
                {:else}
					<tr>
						<td colspan="8" class="text-center">NO EXISTE DETALLE DE ASISTENCIA</td>
					</tr>
				{/if}
			</tbody>
		</table>
	</div>
</div>