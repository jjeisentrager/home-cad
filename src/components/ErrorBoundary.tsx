import { Component, type ReactNode } from 'react'

interface Props { children: ReactNode }
interface State { error: Error | null }

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{
          padding: '20px', background: '#1a0000', color: '#ff6060',
          fontFamily: 'monospace', fontSize: '13px', height: '100%',
          overflowY: 'auto',
        }}>
          <h2 style={{ color: '#ff4040', marginBottom: '12px' }}>Render Error</h2>
          <pre>{this.state.error.message}</pre>
          <pre style={{ marginTop: '12px', fontSize: '11px', color: '#cc4040' }}>
            {this.state.error.stack}
          </pre>
        </div>
      )
    }
    return this.props.children
  }
}
