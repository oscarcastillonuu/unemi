<script lang="ts">

	export let aData;

</script>
<div class="row-fluid">
    <table class="table table-bordered table-striped">
        <thead>
        <tr>
            <th style="text-align: center">Fecha</th>
            <th style="text-align: center">Observación</th>
            <th style="text-align: center">Estado</th>
        </tr>
        </thead>
        <tbody>
        {#each aData.detalle as d }
            <tr>
                <td style="text-align: center;">{d.fecha_creacion} </td>
                <td style="text-align: center">{d.detalle }</td>
                <td style="text-align: center">
                    {#if d.accion == 0}<span  class="label label-default">{d.get_accion }</span>
                    {/if}
                    {#if d.accion == 1}
                        <span  class="label label-important">{d.get_accion }</span>
                    {/if}
                    {#if d.accion == 2}
                        <span class="label label-success">{d.get_accion }</span>
                    {/if}
                    {#if d.accion == 3}
                        <span  class="label label-warning">{d.get_accion }</span>
                    {/if}
                </td>
            </tr>
        {/each}
        </tbody>
    </table>
</div>