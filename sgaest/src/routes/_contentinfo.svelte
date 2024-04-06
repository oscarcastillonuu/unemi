<script lang="ts">
    import { Button, Modal, ModalBody, ModalFooter, ModalHeader } from 'sveltestrap';
	import Insignia from "$components/Alumno/Insignia/Insignia.svelte";
	import { variables } from "$lib/utils/constants";
    export let aData;
    export let mToggle;
    export let saveInsignia;
</script>
<style>
  
.btn-gold {
    border-radius: 20px;
    /*font-size: 12px;*/
    font-weight: 400;
    border-color: #d1ccaf;
    color: #fff;
    /*width: 180px;*/
    padding: 5px 18px 5px 18px;
}

.btn-gold:hover {
    background-color: #d1ccaf;
    color: #fff;
}
</style>
<div class="opacidadno text-center p-1">
    <img class="figure-img img-fluid rounded mb-6" src="{variables.BASE_API}/static/images/icons/texto_insignia_deportes.png" style="width: 290px!important;">
    <img class="figure-img img-fluid rounded mb-4" src="{variables.BASE_API}{aData['insignia'].insignia.modelo}" style="height: 225px;width: 200px;margin-top: -35px;">
    <br><a href="javascript:;" class="btn-gold" style="border-radius:35px;width: 100px;color:white;border:1.5px solid #d1ccaf;" on:click={()=> {saveInsignia(aData['insignia'].id)}}>Cerrar</a>
</div>
