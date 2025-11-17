import { Link } from 'react-router-dom'

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-600 to-primary-800 text-white py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-6xl font-display font-bold mb-6">
              Excel in NCEA & Cambridge Exams
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-primary-100">
              Expert tutoring in Physics, Mathematics, English Literature, and Science
              for Years 9-13 in Auckland
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/booking"
                className="btn btn-accent text-lg px-8 py-4 shadow-lg hover:shadow-xl"
              >
                Book a Free Trial Session
              </Link>
              <Link
                to="/subjects"
                className="btn btn-outline border-white text-white hover:bg-white hover:text-primary-600 text-lg px-8 py-4"
              >
                Explore Subjects
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Success Stats */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">200+</div>
              <div className="text-gray-600">Students Tutored</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">95%</div>
              <div className="text-gray-600">Success Rate</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">5+</div>
              <div className="text-gray-600">Years Experience</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">4.9⭐</div>
              <div className="text-gray-600">Average Rating</div>
            </div>
          </div>
        </div>
      </section>

      {/* Subjects */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-display font-bold text-center mb-12">
            Subjects We Cover
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                title: 'Physics',
                icon: '⚛️',
                description: 'Mechanics, electricity, waves, nuclear physics',
                color: 'bg-blue-500'
              },
              {
                title: 'Mathematics',
                icon: '📐',
                description: 'Algebra, calculus, statistics, geometry',
                color: 'bg-green-500'
              },
              {
                title: 'English Literature',
                icon: '📚',
                description: 'Text analysis, essay writing, critical thinking',
                color: 'bg-purple-500'
              },
              {
                title: 'General Science',
                icon: '🔬',
                description: 'Foundation for Year 9-10 students',
                color: 'bg-orange-500'
              }
            ].map((subject) => (
              <div key={subject.title} className="card hover:shadow-xl transition-shadow">
                <div className={`${subject.color} w-16 h-16 rounded-lg flex items-center justify-center text-3xl mb-4`}>
                  {subject.icon}
                </div>
                <h3 className="text-xl font-bold mb-2">{subject.title}</h3>
                <p className="text-gray-600 mb-4">{subject.description}</p>
                <Link
                  to={`/subjects/${subject.title.toLowerCase().replace(' ', '-')}`}
                  className="text-primary-600 font-medium hover:text-primary-700"
                >
                  Learn More →
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-display font-bold text-center mb-12">
            Why Choose Us?
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: 'Personalized Learning',
                description: 'Customized lesson plans tailored to each student\'s needs and learning style',
                icon: '👤'
              },
              {
                title: 'Exam Expertise',
                description: 'Deep understanding of NCEA and Cambridge assessment structures',
                icon: '🎯'
              },
              {
                title: 'Proven Results',
                description: 'Track record of Excellence/Merit achievements and A*/A grades',
                icon: '🏆'
              },
              {
                title: 'Flexible Scheduling',
                description: 'After-school, evening, and weekend sessions available',
                icon: '📅'
              },
              {
                title: 'Online & In-Person',
                description: 'Choose the format that works best for you',
                icon: '💻'
              },
              {
                title: 'Progress Tracking',
                description: 'Regular reports and ongoing communication with parents',
                icon: '📊'
              }
            ].map((benefit) => (
              <div key={benefit.title} className="text-center">
                <div className="text-5xl mb-4">{benefit.icon}</div>
                <h3 className="text-xl font-bold mb-2">{benefit.title}</h3>
                <p className="text-gray-600">{benefit.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-accent-500 to-accent-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-display font-bold mb-6">
            Ready to Achieve Excellence?
          </h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Book your free trial session today and experience the difference
            expert tutoring can make.
          </p>
          <Link
            to="/booking"
            className="btn bg-white text-accent-600 hover:bg-gray-100 text-lg px-8 py-4 shadow-lg"
          >
            Book Free Trial Now
          </Link>
        </div>
      </section>
    </div>
  )
}
