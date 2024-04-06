<script lang="ts">
    import { Card, CardBody, CardFooter } from 'sveltestrap';
    export let image;
    export let title = "Sin Titulo";
    export let url = "#";
    export  let  className = "mb-4 card-hover";
</script>
<Card  class={className}>
    <slot name="card-header">
        <a href="{url}" class="card-img-top">
            <img src="{image}" alt="" onerror="this.onerror=null;this.src='./image.png'" style="height: 12rem;" class="rounded-top-md card-img-top">
        </a>
    </slot>
    <CardBody>
        <slot name="card-body">
            <h6 class="mb-2 text-wrap" >
                <a href="#" class="text-wrap">{title}</a>
            </h6>
        </slot>
    </CardBody>

    <CardFooter class="p-1">
        <slot name="card-footer">
            <div class="lh-1 text-center">
                <a href="{url}" class="btn btn-sm" style="background:#006dcc; color: white; width: 80%;">
                    <i class="mdi mdi-plus-circle"></i> Ver más
                </a>
            </div>
        </slot>
    </CardFooter>
</Card>
