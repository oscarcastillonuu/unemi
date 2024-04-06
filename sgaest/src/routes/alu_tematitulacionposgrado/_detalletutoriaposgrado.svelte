<script lang="ts">
	import { onMount } from 'svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';
	export let aData;

</script>

<table class=" tabla_responsive  table table-bordered">
    <thead>
    <tr>
        <th style="text-align: center" colspan="6">TUTORÍA</th>
    </tr>

    </thead>
<tbody>
 <tr>
        <th>FECHA REGISTRO:</th>
        <td>{ aData.tutoria.fecharegistro}</td>
        <th>ETAPA TUTORÍA</th>
        <td>{aData.tutoria.programaetapatutoria.etapatutoria.descripcion}</td>
        <th>MODALIDAD:</th>
        <td>{ aData.tutoria.modalidad_display }</td>
    </tr>
    <tr>
        <th>HORA INICIO:</th>
        <td>{ aData.tutoria.horainicio}</td>
        <th>HORA FIN:</th>
        <td>{ aData.tutoria.horafin }</td>
        <th>HORAS DEDICADAS:</th>
        <td>{ aData.tutoria.horas } {#if aData.tutoria.horas == 1} hora {:else} horas {/if}</td>

    </tr>
    <tr>
        <th>ENLACE GRABACIÓN TUTORÍA:</th>
        <td colspan="6">
           {#if aData.tutoria.enlace ==""}
              S/N
           {:else}
           <a style="font-size:11px;" href="{ aData.tutoria.enlace }" target="_blank"><i class="fa fa-video-camera"></i> {  aData.tutoria.enlace }
        </a>
           {/if}
        </td>

    </tr>
 <tr>
        <th style="text-align: center" colspan="6">TÍTULO TUTORIA</th>
    </tr>
 <tr>
     <td colspan="6">{ aData.tutoria.observacion }</td>
 </tr>

 <tr>
        <th style="text-align: center" colspan="6">DETALLE TUTORÍA</th>
    </tr>
 <tr>
     <td colspan="6">{ aData.tutoria.detalle }</td>
 </tr>

</tbody>
</table>
