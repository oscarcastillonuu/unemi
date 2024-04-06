<script lang="ts">
    import { Card, CardBody, CardFooter, Col, Row, Container } from 'sveltestrap';
    export let title;
    export let short_description;
    export let image="https://sga.unemi.edu.ec/media/imagenevento/imagen_evento2021123113350.jpeg";
    export let front_page = "https://sga.unemi.edu.ec/media/imagenportadaevento/imagen_evento2021123151227.png";
    export let url_video;
</script>
<div class="rounded rounded-3 pt-lg-8 pb-lg-16 pt-8 pb-12 bg-primary" style="
								background: url({front_page}) no-repeat;
								background-size: cover;
							">
    <Container>
        <Row class="align-items-center">
            <Col class="col-xl-7 col-lg-7 col-md-12">
                <slot name="content-front-page">
                    <div>
                        <h1 class="text-white display-5 fw-semi-bold">{title}</h1>
                        <p class="text-white mb-6 lead">
                            {@html short_description}
                        </p>
                    </div>
                </slot>
            </Col>
        </Row>
    </Container>
</div>
<div class="pb-10">
    <Container>
        <Row>
            <Col class="col-lg-8 col-md-12 col-12 mt-n8 mb-4 mb-lg-0">
                <Card class="rounded-3">
                    <CardBody>
                        <slot name="card-body-content"></slot>
                    </CardBody>
                </Card>
            </Col>
            <Col class="col-lg-4 col-md-12 col-12 mt-lg-n22">
                <Card class="mb-3 mb-4">
                    <div class="p-1">
                        <div class="d-flex justify-content-evenly position-relative rounded py-10  border-white border rounded-3 bg-cover" style="height: 18rem;background-image: url({image});">
                            {#if url_video}
                                <a class="popup-youtube icon-shape mt-5 rounded-circle btn-play icon-xl text-decoration-none" href="{url_video}">
                                    <i class="fe fe-play"></i>
                                </a>
                            {/if}
                        </div>
                    </div>
                    <CardBody>
                        <slot name="card-body-content2"></slot>
                    </CardBody>
                </Card>
            </Col>
        </Row>
    </Container>
</div>