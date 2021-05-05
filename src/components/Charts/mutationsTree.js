
import React from 'react';
import Container, {Title} from "./styles";

class MutationsTree extends React.Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    createVariants(variants, level){
        let variantLines=[];
        for(const variant of variants){
            variantLines.push('---'.repeat(level)+"variant: "+ variant.name+" (" + variant.mutations.map(mutation=>mutation.from+mutation.position+mutation.to).join(", ")+")");
            if(variant.subs.length>0){
                variantLines=variantLines.concat(this.createVariants(variant.subs, level+1));
            }
        }
        return variantLines;
    }


    componentDidMount() {
        let variantsTree = this.createVariants(this.props.data, 0).map(i => {
            return <p>{i}</p>
        });
        this.setState({data:variantsTree});      
    }

    componentDidUpdate(prevProps) {
        this.render();
    }


    render() {
        return (
            <Container width="90%" ref="">
                <Title>
                    {"Mutations tree"}
                </Title>
                {this.state.data}
                {this.props.renderProp ? this.props.renderProp : null}
            </Container>
        )
    }
}

export default MutationsTree;