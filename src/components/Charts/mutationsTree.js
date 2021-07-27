
import React from 'react';
import Container, {Title} from "./styles";

class MutationsTree extends React.Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    createVariants = (variants, level) => {
        return variants.flatMap((variant) => [
            `${'---'.repeat(level)}variant: ${variant.name} (${variant.mutations.map(mutation=>mutation.from+mutation.position+mutation.to).join(", ")})`,
            ...this.createVariants(variant.subs, level+1)
         ]);
    }

    createVariantWithpTags = (variants) => {
        return this.createVariants(variants, 0).map(i => <p>{i}</p>);
    } 
    
    render() {
        return (
            <Container width="90%" ref="">
                <Title>
                    {"Mutations tree"}
                </Title>
                {this.createVariantWithpTags(this.props.data)}
                {this.props.renderProp ? this.props.renderProp : null}
            </Container>
        )
    }
}

export default MutationsTree;
